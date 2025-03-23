import logging
from typing import Annotated, List

from auth.services import admin_access
from database.core import get_async_db
from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import EventCreate, EventResponse, EventUpdate
from .services import (
    create_new_event,
    delete_event_by_id,
    get_all_events,
    get_event_by_id,
    update_event,
)

logger = logging.getLogger(__name__)

events_router = APIRouter(prefix="/event", tags=["Events"])


@events_router.post(
    "/create",
    summary="create events",
    dependencies=[Depends(admin_access)],
    response_model=EventResponse,
    operation_id="post_create_event",
)
async def create_event(
    event: Annotated[EventCreate, Form()],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    event = await create_new_event(event, db)
    return event


@events_router.get(
    "/events",
    summary="List events",
    response_model=List[EventResponse],
    operation_id="get_events",
)
async def view_events(db: Annotated[AsyncSession, Depends(get_async_db)]):
    events = await get_all_events(db=db)
    return events


@events_router.get(
    "/list/{event_id}",
    summary="List an event using its ID",
    operation_id="get_event_by_id",
)
async def get_events_by_id(
    event_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    student = await get_event_by_id(event_id, db)
    return student


@events_router.patch(
    "/update/{event_id}",
    response_model=EventResponse,
    summary="Update an event using its ID",
    dependencies=[Depends(admin_access)],
    operation_id="patch_update_event_by_id",
)
async def update_events(
    event_id: int,
    updated_event: Annotated[EventUpdate, Form()],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    new_updated_event = await update_event(
        event_id=event_id, event_in=updated_event, db=db
    )
    if new_updated_event:
        return new_updated_event
    else:
        return {"detail": "failed", "user": {}}


@events_router.delete(
    "/delete/{event_id}",
    summary="delete an event using its ID",
    dependencies=[Depends(admin_access)],
    operation_id="delete_event_by_id",
)
async def delete_event(
    event_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    student = await delete_event_by_id(event_id, db)
    return student
