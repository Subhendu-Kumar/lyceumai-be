import os
import uuid
import requests
from getstream import Stream
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List

load_dotenv()

STREAM_API_KEY = os.getenv("STREAM_API_KEY")
STREAM_API_SECRET = os.getenv("STREAM_API_SECRET")

STREAM_TIMEOUT = 10
MEETING_TYPE = "default"
MEETING_API_BASE_URL = "https://chat.stream-io-api.com/video/call"

# stream client
stream_client = Stream(
    api_key=STREAM_API_KEY,
    timeout=STREAM_TIMEOUT,
    api_secret=STREAM_API_SECRET,
)


class CallbackData(BaseModel):
    id: str
    classId: str
    start_time: str
    description: str
    end_time: str | None


class Recording(BaseModel):
    url: str
    date: str
    session_id: str


# create stream token
async def create_stream_token(user_id: str) -> str:
    token = stream_client.create_token(user_id=user_id, expiration=3600)
    return token


async def stream_create_meeting(
    user_id: str,
    class_id: str,
    description: str,
    start_time: str | None = None,
) -> CallbackData:
    unique_meeting_id = uuid.uuid4()

    if start_time is None:
        start_time = f"{datetime.now().isoformat()}Z"

    url = f"{MEETING_API_BASE_URL}/{MEETING_TYPE}/{unique_meeting_id}?api_key={STREAM_API_KEY}"

    token = await create_stream_token(user_id)

    headers = {
        "accept": "application/json",
        "Stream-Auth-Type": "jwt",
        "Authorization": token,
    }

    payload = {
        "data": {
            "custom": {
                "classId": class_id,
                "description": description,
            },
            "video": True,
            "starts_at": start_time,
        },
        "video": True,
    }

    response = requests.post(url, headers=headers, json=payload)

    response.raise_for_status()

    response_data = response.json()

    call = response_data.get("call", {})

    custom = call.get("custom", {})

    return CallbackData(
        id=call.get("id"),
        classId=custom.get("classId"),
        start_time=call.get("starts_at"),
        description=custom.get("description"),
        end_time=call.get("ended_at", None),
    )


async def get_meetings(user_id: str, class_id: str) -> List[CallbackData]:
    try:
        url = f"{MEETING_API_BASE_URL}s?api_key={STREAM_API_KEY}"

        token = await create_stream_token(user_id)

        headers = {
            "accept": "application/json",
            "Stream-Auth-Type": "jwt",
            "Authorization": token,
        }

        payload = {
            "filter_conditions": {
                "custom.classId": class_id,
            },
            "sort": [{"direction": -1, "field": "starts_at"}],
        }

        response = requests.post(url, headers=headers, json=payload)

        response.raise_for_status()

        calls = response.json().get("calls", [])

        calls_data = []
        for c in calls:
            call = c.get("call", {})
            custom = call.get("custom", {})
            calls_data.append(
                CallbackData(
                    id=call.get("id"),
                    classId=custom.get("classId"),
                    end_time=call.get("ended_at"),
                    start_time=call.get("starts_at"),
                    description=custom.get("description"),
                )
            )

        return calls_data
    except Exception as e:
        print(f"Error fetching calls: {e}")
        return []


async def get_recording_by_meet_id(meet_id: str, user_id: str) -> List[Recording]:
    try:
        token = await create_stream_token(user_id=user_id)
        headers = {
            "accept": "application/json",
            "Stream-Auth-Type": "jwt",
            "Authorization": token,
        }
        response = requests.get(
            f"{MEETING_API_BASE_URL}/default/{meet_id}/recordings?api_key={STREAM_API_KEY}",
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
