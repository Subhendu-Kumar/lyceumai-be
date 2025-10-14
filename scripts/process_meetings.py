import os
from dotenv import load_dotenv
import requests
import asyncio
import json
import aiohttp
import subprocess
from io import BytesIO
from pydantic import BaseModel
from typing import List
import assemblyai as aai
from prisma import Prisma
from getstream import Stream
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
            Recording(url=rec.get("url", ""), date=rec.get("end_time", ""))
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


async def main():
    await db.connect()
    meetings = await db.classmeetings.find_many(
        where={"meetingData": {"some": {"transcript": None, "summary": None}}},
    )
    meeting_ids = [{"id": m.id, "meetId": m.meetId} for m in meetings if m.meetId]

    for meet in meeting_ids:
        meet_id = meet["id"]
        meeting_id = meet["meetId"]

        recordings = await get_recordings(meeting_id)

        for recording in recordings:
            url = recording.url
            # date = recording.date
            video_path = f"{meeting_id}.mp4"
            audio_path = f"{meeting_id}.mp3"

            await download_video(url, video_path)
            convert_to_audio(video_path, audio_path)

            transcript_text = await transcribe_file(audio_path)

            print(f"Meeting ID: {meeting_id}")
            print(f"Transcript: {transcript_text}")
            print("\n\n\n")

    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
