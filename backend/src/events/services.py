from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Event
from .schemas import EventCreate, EventUpdate


async def get_all_events(db: AsyncSession) -> List[Event]:
    query = select(Event).where(Event.is_deleted.is_(False))
    event = await db.execute(query)
    return event.scalars().all()


async def create_new_event(event: EventCreate, db: AsyncSession):
    new_event = Event(**event.model_dump())

    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)

    return new_event


async def get_event_by_id(event_id: int, db: AsyncSession) -> Optional[Event]:
    query = select(Event).where(
        Event.id == event_id,
    )
    event = await db.execute(query)

    return event.unique().scalar_one_or_none()


async def update_event(
    event_id: int, event_in: EventUpdate, db: AsyncSession
) -> Optional[Event]:
    event = await get_event_by_id(event_id=event_id, db=db)

    if not event:
        return None

    for field, value in event_in.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    db.add(event)
    await db.commit()
    await db.refresh(event)

    return event


async def delete_event_by_id(event_id: int, db: AsyncSession) -> Optional[Event]:
    event = await get_event_by_id(db=db, event_id=event_id)
    if not event:
        return None

    event.is_deleted = True
    await db.commit()
    await db.refresh(event)

    return event
