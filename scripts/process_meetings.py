# process_meetings.py
# Script to process recorded meetings: download, convert, transcribe, summarize, and store in DB.

# imports
import os
import asyncio
import aiohttp
import requests
import subprocess
import assemblyai as aai
from io import BytesIO
from typing import List
from prisma import Prisma
from getstream import Stream
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
STREAM_API_KEY = os.getenv("STREAM_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
STREAM_API_SECRET = os.getenv("STREAM_API_SECRET")
ASSEMBLY_AI_API_KEY = os.getenv("ASSEMBLY_AI_API_KEY")

# constants
STREAM_TIMEOUT = 10  # seconds
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


# create stream token
def create_stream_token() -> str:
    token = client.create_token(user_id="user-id", expiration=3600)
    return token


# fetch recordings for a meeting
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


# download video file
async def download_video(url: str, output_path: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                with open(output_path, "wb") as f:
                    f.write(await resp.read())
        return True
    except asyncio.TimeoutError:
        print(f"Timeout while downloading {url}")
        return False
    except aiohttp.ClientError as e:
        print(f"Network error while downloading {url}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error while downloading {url}: {e}")
        return False


# convert video to audio using ffmpeg
def convert_to_audio(video_path: str, audio_path: str) -> bool:
    try:
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg failed for {video_path}")
        print(e.stderr)
        return False


# transcribe audio file
async def transcribe_file(audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        file_bytes = f.read()
    transcript = aai_transcriber.transcribe(BytesIO(file_bytes))
    if transcript.status == "error":
        print(f"Transcription error: {transcript.error}")
        return ""
    return transcript.text


# summarize transcript
async def summarize_transcript(transcript: str) -> str:
    chain = summary_template | gemini | parser
    summary = chain.invoke({"transcript": transcript})
    return summary


# main processing function
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

            download_result = await download_video(url, video_path)
            if not download_result:
                print(f"Skipping meeting — failed to download from {url}")
                continue

            conversion_result = convert_to_audio(video_path, audio_path)
            if not conversion_result:
                print(
                    f"Skipping meeting — failed to convert video to audio for {video_path}"
                )
                continue

            transcript_text = await transcribe_file(audio_path)
            if not transcript_text:
                print(f"Skipping meeting — failed to transcribe audio for {audio_path}")
                continue
            else:
                summary_text = await summarize_transcript(transcript_text)
                if not summary_text:
                    print(
                        f"Skipping meeting — failed to summarize transcript for {audio_path}"
                    )
                    continue

            await db.meetingdata.create(
                data={
                    "sessionId": session_id,
                    "summary": summary_text,
                    "classMeetingId": meet_id,
                    "transcript": transcript_text,
                    "meetingCompletionTime": meet_date,
                }
            )

    await db.disconnect()


# entry point
if __name__ == "__main__":
    asyncio.run(main())
