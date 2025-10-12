from pydantic import BaseModel
from enum import Enum


class MeetingStatus(str, Enum):
    ONGOING = "ONGOING"
    CANCELED = "CANCELED"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"


class CreateMeeting(BaseModel):
    meetId: str
    classroomId: str
    meetStatus: MeetingStatus
    MeetingTime: str  # ISO 8601 format
