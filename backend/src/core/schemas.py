from datetime import (
    date,
    datetime,  # noqa: F401
)
from typing import List, Optional, Union  # noqa: F401

from application.schemas import ApplicationResponse
from pydantic import (  # noqa: F401
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)
from subject.schemas import SubjectResponse

from core.enums import EducationLevel, Gender

from .enums import Role  # noqa: F401

# schemas.py


class Message(BaseModel):
    content: str


class MessageCreate(BaseModel):
    teacher_id: str
    sender: str
    content: str


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone_number: str

    # @field_validator("password")
    # def password_not_username(cls, password, info):
    #     email = info.data.get("email")
    #     if email and email in password:
    #         raise ValueError("Password cannot contain email")

    #     return password


class UserPasswordUpdate(BaseModel):
    new_password: str


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    role: Role
    phone_number: Optional[str]
    id_number: Optional[str]
    gender: Optional[Gender]
    date_of_birth: Optional[date]
    number_of_passed_subjects: Optional[int]
    previous_school: Optional[str]
    next_of_kin: Optional[str]
    subjects: Optional[List[SubjectResponse]]
    application: Optional[ApplicationResponse]
    current_academic_level: Optional[EducationLevel]
    is_deleted: bool
    is_active: bool
    is_verified: bool
    created_at: Union[None, datetime] = None

    model_config = ConfigDict(from_attributes=True)
