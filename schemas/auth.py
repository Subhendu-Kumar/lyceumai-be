from enum import Enum
from pydantic import BaseModel, EmailStr


class RoleEnum(str, Enum):
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"


class SignupUser(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleEnum


class LoginUser(BaseModel):
    email: EmailStr
    password: str
