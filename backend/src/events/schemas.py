from datetime import date, time
from typing import Optional

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    name: str
    date: date


class EventResponse(BaseModel):
    name: str
    date: date


class EventUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the event")
    date: date
    