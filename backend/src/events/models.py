from database.core import Base
from sqlalchemy import Date, Integer, String, Time, func
from sqlalchemy.orm import Mapped, mapped_column


class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    date: Mapped[Date] = mapped_column(Date, default=func.now())
