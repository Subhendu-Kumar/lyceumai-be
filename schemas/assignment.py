from pydantic import BaseModel
from enum import Enum


class AssignmentTypeEnum(str, Enum):
    TEXT = "TEXT"
    VOICE = "VOICE"


class AssignmentBase(BaseModel):
    title: str
    dueDate: str
    description: str
    type: AssignmentTypeEnum


class TextAssignmentSubmission(BaseModel):
    content: str
