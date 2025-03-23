from database.core import Base
from sqlalchemy import Enum, ForeignKey, Integer,String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .enums import ApplicationStatus


class Application(Base):
    __tablename__ = "application"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.SENT, index=True
    )

    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False, index=True
    )
    combination: Mapped[str] = mapped_column(String, nullable=True, index=True)
    applicant = relationship("User", back_populates="application", lazy="selectin")

    subjects = relationship(
        "Subject",
        back_populates="application",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
