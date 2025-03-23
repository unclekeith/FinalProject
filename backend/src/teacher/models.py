from database.core import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), index=True)

    # Relationship to messages and conversation
    messages = relationship(
        "Messages", back_populates="teacher", cascade="all, delete-orphan"
    )
    conversation = relationship("Conversation", back_populates="teacher", uselist=False)


class Messages(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), index=True)
    sender = Column(String)  # "teacher" or "admin"
    content = Column(Text)
    timestamp = Column(DateTime, default=func.now())  # Correct usage of func.now()

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    teacher = relationship("Teacher", back_populates="messages")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    messages = relationship(
        "Messages", back_populates="conversation", cascade="all, delete-orphan"
    )
    teacher = relationship("Teacher", back_populates="conversation")


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
