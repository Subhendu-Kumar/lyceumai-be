from enum import Enum
from pydantic import BaseModel
from typing import Optional


class MeetingStatus(str, Enum):
    ONGOING = "ONGOING"
    CANCELED = "CANCELED"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"


class CreateMeeting(BaseModel):
    description: str
    classroomId: str
    meetStatus: MeetingStatus
    meetingTime: Optional[str] = None
