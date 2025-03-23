import logging
from datetime import datetime
from typing import AsyncGenerator

from core.config import settings
from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

logger = logging.getLogger(__name__)


async_engine = create_async_engine(
    settings.DATABASE_URL,
)
AsyncSessionLocal = async_sessionmaker(bind=async_engine)


class RemoveBaseFieldMixin:
    created_at: None
    updated_at: None
    is_deleted: None


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    # TODO: find a way to not create a schema each time a table is created

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}


async def init_models():
    async with async_engine.begin() as async_conn:
        await async_conn.run_sync(Base.metadata.create_all)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    await init_models()
    async_session = async_sessionmaker(async_engine, expire_on_commit=False)

    try:
        async with async_session() as session:
            yield session
    finally:
        await session.close()
