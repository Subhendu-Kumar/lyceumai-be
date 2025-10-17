import os
import json
import asyncio
import aiohttp
import requests
import subprocess
from io import BytesIO
from typing import List
import assemblyai as aai
from prisma import Prisma
from getstream import Stream
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

STREAM_TIMEOUT = 10  # seconds
DATABASE_URL = os.getenv("DATABASE_URL")
STREAM_API_KEY = os.getenv("STREAM_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
STREAM_API_SECRET = os.getenv("STREAM_API_SECRET")
ASSEMBLY_AI_API_KEY = os.getenv("ASSEMBLY_AI_API_KEY")
MEETING_API_BASE_URL = "https://chat.stream-io-api.com/video/call"

# aai settings
aai.settings.api_key = ASSEMBLY_AI_API_KEY
aai_config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.best)
aai_transcriber = aai.Transcriber(config=aai_config)

# gemini settings
gemini = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# db settings
db = Prisma()

# stream settings
client = Stream(
    api_key=STREAM_API_KEY,
    timeout=STREAM_TIMEOUT,
    api_secret=STREAM_API_SECRET,
)


# models
class Recording(BaseModel):
    url: str
    date: str
    session_id: str


# prompt
summary_template = PromptTemplate(
    input_variables=["transcript"],
    template="""
    You are an expert meeting summarizer.
    Your task is to analyze the following meeting transcript and generate a clear, structured summary.

    Transcript: {transcript}

    Your summary should include:
        Meeting Title / Topic – What the meeting was mainly about.
        Date & Participants (if mentioned) – Who attended.
        Key Discussion Points – Main topics covered.
        Decisions Made – Summarize any decisions or agreements.
        Action Items – Tasks assigned, with responsible persons (if stated).
        Unresolved Issues / Follow-ups – Pending items or questions for next meeting.
        Overall Summary (3–5 sentences) – A concise paragraph summarizing the meeting outcome.
    """,
)


# output parser
parser = StrOutputParser()


def create_stream_token() -> str:
    token = client.create_token(user_id="user-id", expiration=3600)
    return token


async def get_recordings(meeting_id: str) -> List[Recording]:
    try:
        token = create_stream_token()
        headers = {
            "accept": "application/json",
            "Stream-Auth-Type": "jwt",
            "Authorization": token,
        }
        response = requests.get(
            f"{MEETING_API_BASE_URL}/default/{meeting_id}/recordings?api_key={STREAM_API_KEY}",
            headers=headers,
        )
        response.raise_for_status()
        recordings = [
            Recording(
                url=rec.get("url", ""),
                date=rec.get("end_time", ""),
                session_id=rec.get("session_id", ""),
            )
            for rec in response.json().get("recordings", [])
        ]
        return recordings
    except Exception as e:
        print(f"Error fetching recordings: {e}")
        return []


async def download_video(url: str, output_path: str) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            with open(output_path, "wb") as f:
                f.write(await resp.read())


def convert_to_audio(video_path: str, audio_path: str) -> None:
    subprocess.run(
        ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path], check=True
    )


async def transcribe_file(audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        file_bytes = f.read()
    transcript = aai_transcriber.transcribe(BytesIO(file_bytes))
    if transcript.status == "error":
        print(f"Transcription error: {transcript.error}")
        return ""
    return transcript.text


async def summarize_transcript(transcript: str) -> str:
    chain = summary_template | gemini | parser
    summary = chain.invoke({"transcript": transcript})
    return summary


async def main():
    await db.connect()
    meetings = await db.classmeetings.find_many(
        where={"meetingData": {"none": {}}},
    )
    meeting_ids = [{"id": m.id, "meetId": m.meetId} for m in meetings if m.meetId]

    for meet in meeting_ids:
        meet_id = meet["id"]
        meeting_id = meet["meetId"]

        recordings = await get_recordings(meeting_id)

        for recording in recordings:
            url = recording.url
            meet_date = recording.date
            session_id = recording.session_id

            video_path = os.path.join(f"{meeting_id}.mp4")
            audio_path = os.path.join(f"{meeting_id}.mp3")

            await download_video(url, video_path)
            convert_to_audio(video_path, audio_path)

            transcript_text = await transcribe_file(audio_path)

            if not transcript_text:
                transcript_text = "failed to get transcript"
                summary_text = "no transcript available"
            else:
                summary_text = await summarize_transcript(transcript_text)
                if not summary_text:
                    summary_text = "failed to summarize transcript"

            await db.meetingdata.create(
                data={
                    "sessionId": session_id,
                    "classMeetingId": meet_id,
                    "transcript": transcript_text,
                    "summary": summary_text,
                    "meetingCompletionTime": meet_date,
                }
            )

            print(f"Recording URL: {url}")
            print(f"Summary: {summary_text}")
            print(f"Meeting ID: {meeting_id}")
            print(f"Transcript: {transcript_text}")
            print("\n\n\n")

    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
