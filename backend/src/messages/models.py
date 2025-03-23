from enum import Enum as PyEnum

from database.core import Base
from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Status(PyEnum):
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    READ = "READ"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[PyEnum] = mapped_column(Enum(Status), default=Status.SENT)
