from database.core import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Events(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    start_time: Mapped[str] = mapped_column(Integer, nullable=True)
    end_time: Mapped[str] = mapped_column(Integer, nullable=True)
    date: Mapped[int] = mapped_column(Integer, nullable=True)
    participation: Mapped[str] = mapped_column(String, nullable=True)
    alerts: Mapped[str] = mapped_column(String, nullable=True)
