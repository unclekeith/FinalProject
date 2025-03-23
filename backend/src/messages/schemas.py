from pydantic import BaseModel

from .models import Status


class MessageCreate(BaseModel):
    message: str


class MessageResponse(BaseModel):
    message: str
    status: Status


class MessageUpdate(BaseModel):
    message: str


class MessageStatusUpdate(BaseModel):
    status: Status
