import logging
from typing import Annotated

from auth.services import admin_access
from database.core import get_async_db
from fastapi import APIRouter, Depends, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Message
from .schemas import MessageCreate, MessageResponse, MessageUpdate
from .services import (
    get_message_by_id,
    remove_message_by_id,
    send_message,
    update_messages,
)

logger = logging.getLogger(__name__)

message_router = APIRouter(prefix="/message", tags=["Messages"])


@message_router.post(
    "/",
    summary="send all message",
    dependencies=[Depends(admin_access)],
    operation_id="post_send_message",
)
async def post_send_message(
    message: MessageCreate, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    mssg = await send_message(message, db)
    return mssg


@message_router.get("/", summary="List messages", operation_id="get_messages")
async def get_messages(db: Annotated[AsyncSession, Depends(get_async_db)]):
    messages = await db.execute(select(Message))
    messages = messages.scalars().all()
    return messages


@message_router.get(
    "/{message_id}",
    summary="List a message using its ID",
    operation_id="get_message_by_id",
)
async def get_messages_by_id(
    message_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    message = await get_message_by_id(message_id, db)
    return message


@message_router.patch(
    "/update/{message_id}",
    response_model=Annotated[MessageResponse, Form()],
    summary="Update a message using its ID",
    dependencies=[Depends(admin_access)],
    operation_id="patch_update_message_by_id",
)
async def update_message(
    message_id: int,
    updated_message: Annotated[MessageUpdate, Form()],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    new_updated_message = await update_messages(
        message_id=message_id, message_in=updated_message, db=db
    )
    if new_updated_message:
        return new_updated_message
    else:
        return {"detail": "failed", "user": {}}


@message_router.delete(
    "/delete/{message_id}",
    summary="delete a message using its ID",
    dependencies=[Depends(admin_access)],
    operation_id="delete_message_by_id",
)
async def delete_message(
    message_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    message = await remove_message_by_id(message_id, db)
    return message
