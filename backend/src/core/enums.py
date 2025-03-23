from enum import Enum as PyEnum


class Permission(PyEnum):
    READ = "READ"
    WRITE = "WRITE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class Role(PyEnum):
    STUDENT = "STUDENT"
    PARENT = "PARENT"
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"


class Gender(PyEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class EducationLevel(PyEnum):
    O_LEVEL = "O_LEVEL"
    A_LEVEL = "A_LEVEL"
    OTHER = "OTHER"  # assigned to distinguish admin users as they cannot be assigned an academic Level


class TeacherEducationLevel(PyEnum):
    DIPLOMA = "DIPLOMA"
    DEGREE = "DEGREE"
    MASTERS = "MASTERS"  # assigned to distinguish admin users as they cannot be assigned an academic Level
    PHD = "PHD"  # assigned to distinguish admin users as they cannot be assigned an academic Level
