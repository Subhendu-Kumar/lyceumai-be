import os
import uuid
import requests
import datetime
from dotenv import load_dotenv
from utils.stream_util import create_stream_token, get_meetings, get_recording_by_meet_id
import asyncio

load_dotenv()

STREAM_API_KEY = os.getenv("STREAM_API_KEY")

unique_id = uuid.uuid4()

meeting_type = "default"

MEETING_API_BASE_URL = "https://chat.stream-io-api.com/video/call"


async def test_create_video_call():
    url = f"{MEETING_API_BASE_URL}/{meeting_type}/{unique_id}?api_key={STREAM_API_KEY}"

    token = await create_stream_token("36e46a5f-8037-42b6-a957-da8db3894680")

    headers = {
        "accept": "application/json",
        "Stream-Auth-Type": "jwt",
        "Authorization": token,
    }

    payload = {
        "data": {
            "created_by": {
                "name": "subhendu kumar dutta",
            },
            "custom": {
                "classId": "baad0fee-7518-4b13-9aa6-a3f7ba666e47",
                "description": "new meeting for discussing project requirements",
            },
            "video": True,
            "starts_at": datetime.datetime.now().isoformat() + "Z",
        },
        "video": True,
    }

    # Send POST request
    response = requests.post(url, headers=headers, json=payload)

    # Raise an error for failed responses
    response.raise_for_status()

    response_data = response.json()

    call = response_data.get("call", {})
    custom = call.get("custom", {})

    print(
        {
            "id": call.get("id"),
            "classId": custom.get("classId"),
            "start_time": call.get("starts_at"),
            "description": custom.get("description"),
        }
    )


if __name__ == "__main__":
    asyncio.run(
        get_recording_by_meet_id("624c831c-5f10-46db-8143-c4cdd21fdc07")
    )
