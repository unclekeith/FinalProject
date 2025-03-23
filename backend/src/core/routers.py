import logging
from typing import Annotated

from auth.services import admin_access, password_reset
from auth.utils import get_current_user
from database.core import get_async_db

# core_router.py
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from student.services import set_student_account_status
from teacher.schemas import (
    ChatHistoryResponse,
    ConversationResponse,
    MessageCreate,
    MessageSchema,
)
from teacher.services import get_all_conversations, get_chat_history, save_message

from .models import User
from .schemas import UserPasswordUpdate

# from .services import get_all_conversations, get_chat_history, save_message

core_router = APIRouter(tags=["Core"])

logger = logging.getLogger(__name__)


@core_router.get("/all-conversations/", response_model=ConversationResponse)
async def get_all_conversations_endpoint(db: AsyncSession = Depends(get_async_db)):
    conversations = await get_all_conversations(db)
    return {
        "conversations": [conversation.teacher_id for conversation in conversations]
    }


@core_router.get("/chat-history/{teacher_id}", response_model=ChatHistoryResponse)
async def get_teacher_chat_history(
    teacher_id: int, db: AsyncSession = Depends(get_async_db)
):
    messages = await get_chat_history(db, teacher_id)
    if not messages:
        raise HTTPException(status_code=404, detail="No chat history found")
    return {"teacher_id": teacher_id, "messages": messages}


@core_router.post("/reply/{teacher_id}")
async def reply_to_teacher(
    teacher_id, response: MessageSchema, db: AsyncSession = Depends(get_async_db)
):
    message_data = MessageCreate(
        teacher_id=teacher_id, sender="admin", content=response.content
    )
    await save_message(db, message_data)
    return {"status": "Reply sent to teacher"}


@core_router.get("/healthcheck", name="healthcheck", operation_id="get_healthcheck")
async def healthcheck():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "STATUS_OK"})


@core_router.post(
    "/deactivate_or_reactivate/{student_id}",
    name="student_deactivate/reactivate",
    dependencies=[Depends(admin_access)],
    operation_id="post_activate_deactivate_user",
)
async def deactivate_reactivate_student_account(
    request: Request,
    student_id: Annotated[int, None],
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    # """Activate / Deactivate an studentaccount."""
    try:
        studentaccount = await set_student_account_status(db=db, id=student_id)
        logger.warning("warning studentaccount deactivated")
        return studentaccount

    except Exception:
        return {"detail": "Could not Activate/ Deactivate account"}


@core_router.patch(
    "/reset-password/{email}",
    summary="Reset user password",
    operation_id="patch_reset_password",
)
async def reset_account(
    email: str,
    updated_password: UserPasswordUpdate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    updated_user = await password_reset(
        email=email,  # Pass the email correctly
        updated_password=updated_password,
        db=db
    )
    if updated_user:
        return {"detail": "Password reset successfully."}  # Return a success message
    else:
        raise HTTPException(
            status_code=404,
            detail="User not found or password reset failed."
        )




@core_router.get("/me", operation_id="get_me")
async def read_user_profile(
    request: Request, current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


# @core_router.get("/all-conversations/")
# async def get_all_conversations_endpoint(db: AsyncSession = Depends(get_async_db)):
#     conversations = await get_all_conversations(db)
#     return {
#         "conversations": [conversation.teacher_id for conversation in conversations]
#     }


# @core_router.get("/chat-history/{teacher_id}")
# async def get_teacher_chat_history(
#     teacher_id: str, db: AsyncSession = Depends(get_async_db)
# ):
#     messages = await get_chat_history(db, teacher_id)
#     if not messages:
#         raise HTTPException(status_code=404, detail="No chat history found")
#     return {"teacher_id": teacher_id, "messages": [msg.content for msg in messages]}


# @core_router.post("/reply/{teacher_id}")
# async def reply_to_teacher(
#     teacher_id: str, response: MessageSchema, db: AsyncSession = Depends(get_async_db)
# ):
#     message_data = MessageCreate(
#         teacher_id=teacher_id, sender="admin", content=response.content
#     )
#     await save_message(db, message_data)
#     return {"status": "Reply sent to teacher"}
