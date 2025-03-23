from typing import List

from core.enums import Gender, TeacherEducationLevel
from pydantic import BaseModel


class MessageSchema(BaseModel):
    content: str


class MessageCreate(BaseModel):
    teacher_id: int
    sender: str  # "teacher" or "admin"
    content: str


class MessageResponse(BaseModel):
    content: str
    sender: str

    class Config:
        orm_mode = True


class ChatHistoryResponse(BaseModel):
    teacher_id: int
    messages: List[MessageResponse]


class ReplyResponse(BaseModel):
    teacher_id: int
    replies: List[MessageResponse]


class ConversationResponse(BaseModel):
    conversations: List[int]  # List of teacher IDs with conversations


class TeacherUpdate(BaseModel):
    teaching_subject: str
    teacher_id_number: str
    teacher_gender: Gender
    teacher_next_of_kin: str
    teacher_current_academic_level: TeacherEducationLevel


class Response(BaseModel):
    admin_id: str = "admin"
    content: str
