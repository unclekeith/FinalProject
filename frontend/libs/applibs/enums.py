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
    BURSUR = "BURSUR"
