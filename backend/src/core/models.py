from typing import Optional

from database.core import Base
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Integer,
    String,
    ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.associations import UserSubjectAssociation  # noqa: F401

from .enums import (
    EducationLevel,
    Gender,  # Assuming you create a Gender Enum
    Role,
    TeacherEducationLevel,
)
from sqlalchemy.sql import func



class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String(length=20))
    last_name: Mapped[Optional[str]] = mapped_column(String(length=20), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(
        String(length=15), unique=True, nullable=True
    )
    id_number: Mapped[Optional[str]] = mapped_column(
        String(length=20), unique=True, nullable=True
    )
    gender: Mapped[Optional[Gender]] = mapped_column(Enum(Gender), nullable=True)
    date_of_birth: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    number_of_passed_subjects: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    previous_school: Mapped[Optional[str]] = mapped_column(
        String(length=100), nullable=True
    )
    next_of_kin: Mapped[Optional[str]] = mapped_column(String(length=50), nullable=True)
    current_academic_level: Mapped[Optional[EducationLevel]] = mapped_column(
        Enum(EducationLevel), nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.STUDENT, index=True)
    teaching_subject: Mapped[Optional[str]] = mapped_column(
        String(length=10), nullable=True
    )
    teacher_id_number: Mapped[Optional[str]] = mapped_column(
        String(length=20), unique=True, nullable=True
    )
    teacher_gender: Mapped[Optional[Gender]] = mapped_column(
        Enum(Gender), nullable=True
    )
    teacher_next_of_kin: Mapped[Optional[str]] = mapped_column(
        String(length=50), nullable=True
    )
    teacher_current_academic_level: Mapped[Optional[TeacherEducationLevel]] = (
        mapped_column(Enum(TeacherEducationLevel), nullable=True)
    )
    is_checked_out = Column(Boolean, default=False)
    last_checked_in = Column(DateTime, nullable=True)
    last_checked_out = Column(DateTime, nullable=True)


    profile_pictures = relationship("ProfilePicture", back_populates="user", cascade="all, delete-orphan")
    certificates = relationship("Certificates", back_populates="user", cascade="all, delete-orphan")


    application = relationship(
        "Application",
        back_populates="applicant",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    subject_associations = relationship(
        "UserSubjectAssociation", back_populates="user", lazy="selectin"
    )
    subjects = relationship(
        "Subject",
        secondary="user_subject",
        back_populates="students",
        lazy="selectin",
        overlaps="subject_associations",
    )

class Certificates(Base):
    __tablename__ = "certificate"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("user.id"))

    # Relationship to User
    user = relationship("User", back_populates="certificates")
class ProfilePicture(Base):
    __tablename__ = "profilepicture"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    # Foreign key for the user
    user_id = Column(Integer, ForeignKey("user.id"))

    # Relationship to User
    user = relationship("User", back_populates="profile_pictures")