from pydantic import BaseModel, EmailStr


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
