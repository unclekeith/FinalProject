from datetime import date

from core.enums import EducationLevel, Gender
from pydantic import BaseModel


class StudentUpdate(BaseModel):
    date_of_birth: date
    id_number: str
    number_of_passed_subjects: int
    gender: Gender
    previous_school: str
    next_of_kin: str
    current_academic_level: EducationLevel


class StudentReactivateDeactivateSchema(BaseModel):
    # id: int
    is_active: bool
