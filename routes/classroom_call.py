from getstream import Stream
import os
from dotenv import load_dotenv

load_dotenv()

STREAM_API_KEY = os.getenv("STREAM_API_KEY")
STREAM_API_SECRET = os.getenv("STREAM_API_SECRET")
STREAM_TIMEOUT = 10.0

stream_client = Stream(
    api_key=STREAM_API_KEY, api_secret=STREAM_API_SECRET, timeout=STREAM_TIMEOUT
)


def create_call():
    call = stream_client.video.call("default", "bed62777-84d0-47cf-ab99-8afc0ce629")

    # Add creator info
    call.get_or_create(
        data={
            "created_by_id": "admin_123",  # 👈 put your teacher/admin user id here
            "custom": {
                "topic": "Math Lecture",
                "duration": "45min",
            },  # optional metadata
        }
    )


if __name__ == "__main__":
    create_call()
