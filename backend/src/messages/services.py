from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Message
from .schemas import MessageUpdate


async def get_all_messages(db: AsyncSession) -> Optional[List[Message]]:
    query = select(Message).where(
        and_(and_(Message.is_deleted.is_("messge")), Message.is_deleted.is_(False)),
    )
    # query = select(Message).where(Message.message.is_("messge"))
    users = await db.execute(query)
    return users.scalars().all()


async def send_message(message: str, db: AsyncSession):
    new_message = Message(
        message=message.message,
    )

    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)

    return new_message


async def get_message_by_id(message_id: int, db: AsyncSession) -> Optional[Message]:
    query = select(Message).where(
        Message.id == message_id,
    )
    user = await db.execute(query)
    return user.scalar_one_or_none()


async def update_messages(
    message_id: int, message_in: MessageUpdate, db: AsyncSession
) -> Optional[Message]:
    message = await get_message_by_id(message_id=message_id, db=db)

    if not message:
        return None

    for field, value in message_in.model_dump(exclude_unset=True).items():
        setattr(message, field, value)

    db.add(message)
    await db.commit()
    await db.refresh(message)

    return message


async def remove_message_by_id(message_id: int, db: AsyncSession) -> Optional[Message]:
    query = select(Message).where(Message.id == message_id)
    res = await db.execute(query)
    message = res.scalar_one_or_none()
    if not message:
        return None
    message.is_deleted = True
    message.updated_at = datetime.now()
    await db.commit()
    await db.refresh(message)
    return message
