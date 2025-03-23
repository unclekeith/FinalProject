from enum import Enum


class ApplicationStatus(Enum):
    SENT = "SENT"
    PENDING = "PENDING"
    RECEIVED = "RECEIVED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
