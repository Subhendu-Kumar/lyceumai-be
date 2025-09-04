from pydantic import BaseModel, EmailStr, Field
from typing import Literal, List


class CreateOrUpdateClassRoom(BaseModel):
    name: str
    description: str


class AddStudentToClass(BaseModel):
    email: EmailStr
    class_id: str


class RemoveStudentFromClass(BaseModel):
    student_id: str
    class_id: str


class ClassAnnouncementCreate(BaseModel):
    title: str
    message: str
    class_id: str


class ClassAnnouncementUpdate(BaseModel):
    title: str
    message: str


class ClassQuizBody(BaseModel):
    title: str
    topic: str
    class_id: str
    description: str
    number_of_questions: int
    difficulty: Literal["EASY", "MEDIUM", "HARD"]


class Question(BaseModel):
    question: str = Field(..., description="The quiz question")
    options: List[str] = Field(..., description="List of answer options")
    answer: int = Field(..., description="The correct answer index (0-based)")


class QuizResponse(BaseModel):
    title: str = Field(..., description="The title of the quiz")
    description: str = Field(..., description="The description of the quiz")
    questions: List[Question] = Field(..., description="List of quiz questions")
