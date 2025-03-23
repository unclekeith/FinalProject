from core.associations import UserSubjectAssociation  # noqa: F401
from database.core import Base
from sqlalchemy import Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .enums import Grades, SubjectNames  # Ensure Grades is correctly imported


class Subject(Base):
    __tablename__ = "subject"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[SubjectNames] = mapped_column(
        Enum(SubjectNames), default=SubjectNames.MATHS
    )
    grade: Mapped[Grades] = mapped_column(
        Enum(Grades), default=Grades.X
    )  # Use Grades enum

    application_id: Mapped[int] = mapped_column(
        ForeignKey("application.id"), nullable=True, index=True
    )
    application = relationship(
        "Application", back_populates="subjects", lazy="selectin"
    )

    user_associations = relationship(
        "UserSubjectAssociation", back_populates="subject", lazy="selectin"
    )
    students = relationship(
        "User",
        secondary="user_subject",
        back_populates="subjects",
        lazy="selectin",
        overlaps="user_associations",
    )
