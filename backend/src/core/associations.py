from database.core import Base
from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from subject.enums import Grades


# Association table with extra fields
class UserSubjectAssociation(Base):
    __tablename__ = "user_subject"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), primary_key=True
    )
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subject.id", ondelete="CASCADE"), primary_key=True
    )
    grade: Mapped[Grades] = mapped_column(Enum(Grades))  # Add the 'grade' column

    user = relationship("User", back_populates="subject_associations")
    subject = relationship("Subject", back_populates="user_associations")
