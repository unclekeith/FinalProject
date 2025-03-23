from typing import List

from pydantic import BaseModel, ConfigDict

from .enums import Grades, SubjectNames


class SubjectCreate(BaseModel):
    name: SubjectNames
    grade: Grades


class CallRequest(BaseModel):
    caller_id: str
    receiver_id: str


class SubjectsCreate(BaseModel):
    subjects: List[SubjectCreate]  # Wrap the list in 'subjects' attribute


class SubjectUpdate(BaseModel):
    name: SubjectNames
    grade: Grades


class SubjectResponse(BaseModel):
    name: SubjectNames
    grade: Grades

    model_config = ConfigDict(from_attributes=True)
