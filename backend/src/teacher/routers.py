import logging
import os
from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Messages, Teacher  # Assuming you have models for Message and Teacher
from .schemas import MessageSchema  # Assuming you have a schema for messages
from auth.services import admin_access, get_current_user
from core.enums import Role
from core.models import User
from database.core import get_async_db
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from teacher.schemas import (
    ChatHistoryResponse,
    MessageCreate,
    MessageSchema,
    ReplyResponse,
)
from teacher.services import get_chat_history, get_replies, save_message

from .models import File as FileModel
from .schemas import TeacherUpdate
from .services import (
    check_in_teacher,
    check_out_teacher,
    get_teacher_account_by_id,
    list_uploaded_files,
    remove_teacher_by_id,
    update_teacher_account,
)

logger = logging.getLogger(__name__)
teacher_router = APIRouter(prefix="/teacher", tags=["Teachers"])


@teacher_router.post("/send-message/")
async def send_message(
    teacher_id, message: MessageSchema, db: AsyncSession = Depends(get_async_db)
):
    message_data = MessageCreate(
        teacher_id=teacher_id, sender="teacher", content=message.content
    )
    await save_message(db, message_data)
    return {"status": "Message sent to admin"}

@teacher_router.get("/teachers-who-sent-messages/")
async def get_all_messages(db: AsyncSession = Depends(get_async_db)):
    # Query to get all messages sent by teachers
    stmt = select(Messages).order_by(Messages.timestamp.desc())
    result = await db.execute(stmt)

    # Fetch all messages
    messages = result.scalars().all()

    if not messages:
        return {"message": "No messages sent yet"}
    
    # Prepare a list of teacher IDs and their messages
    response = [{"teacher_id": message.teacher_id, "content": message.content, "timestamp": message.timestamp} for message in messages]

    return {"messages": response}

@teacher_router.get("/chat-history/", response_model=ChatHistoryResponse)
async def chat_history(teacher_id: int, db: AsyncSession = Depends(get_async_db)):
    messages = await get_chat_history(db, teacher_id)
    if not messages:
        raise HTTPException(status_code=404, detail="No chat history found")
    return {"teacher_id": teacher_id, "messages": messages}


@teacher_router.get("/get-replies/", response_model=ReplyResponse)
async def get_replies_endpoint(
    teacher_id: int, db: AsyncSession = Depends(get_async_db)
):
    replies = await get_replies(db, teacher_id)
    if not replies:
        raise HTTPException(status_code=404, detail="No replies found")
    return {"teacher_id": teacher_id, "replies": replies}


class Document(BaseModel):
    filename: str
    file: bytes


@teacher_router.get(
    "/",
    summary="List user accounts",
    dependencies=[Depends(admin_access)],
    operation_id="get_teachers",
)
async def get_useraccounts(db: Annotated[AsyncSession, Depends(get_async_db)]):
    query = select(User).where(User.role == Role.TEACHER)
    users = await db.execute(query)
    users = users.scalars().all()
    return users


@teacher_router.get(
    "/{teacher_id}",
    summary="Detail a account using its ID",
    dependencies=[Depends(admin_access)],
    operation_id="get_teacher_by_id",
)
async def get_teacher_by_id(
    teacher_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    teacher = await get_teacher_account_by_id(teacher_id, db)
    return teacher


@teacher_router.patch(
    "/update/{teacher_id}",
    summary="Update a user account using its ID",
    operation_id="patch_update_teacher",
)
async def update_useraccount(
    current_user: Annotated[User, Depends(get_current_user)],
    updated_teacher: TeacherUpdate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    new_updated_teacher = await update_teacher_account(
        teacher_id=current_user.id, teacher_in=updated_teacher, db=db
    )
    if not new_updated_teacher:
        raise HTTPException(
            status_code=404, detail="Teacher not found or update failed."
        )

    return new_updated_teacher


@teacher_router.delete(
    "/delete/{teacher_id}",
    summary="delete a user account using its ID",
    dependencies=[Depends(admin_access)],
    operation_id="delete_teacher_by_id",
)
async def delete_useraccount(
    id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    teacher = await remove_teacher_by_id(id, db)
    return teacher


@teacher_router.patch(
    "/Check_In/{teacher_id}",
    summary="Check staff in using their ID",
    operation_id="check_in_staff_by_id",
)
async def check_inn(
    teacher_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    # Call the service function to check in the teacher
    updated_teacher = await check_in_teacher(teacher_id=teacher_id, db=db)

    # Return a success message along with the updated teacher details
    return {"message": "Teacher checked in successfully.", "teacher": updated_teacher}


@teacher_router.patch(
    "/Check_Out/{teacher_id}",
    summary="Check staff out using its ID",
    operation_id="check_out_staff_by_id",
)
async def check_outt(
    teacher_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    success = await check_out_teacher(teacher_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Teacher not found")

    return {"detail": "Teacher checked out successfully", "teacher_id": teacher_id}


@teacher_router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...), db: AsyncSession = Depends(get_async_db)
):
    try:
        # Step 1: Save file to the file system
        contents = await file.read()
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(contents)

        # Step 2: Save file metadata to the database
        new_file = FileModel(filename=file.filename, filepath=file_path)
        db.add(new_file)
        await db.commit()
        await db.refresh(new_file)

        return {"filename": new_file.filename, "file_id": new_file.id}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@teacher_router.get("/list/")
async def list_files(db: AsyncSession = Depends(get_async_db)):
    """
    Fetch the list of uploaded files from the database.
    """
    try:
        # Fetch files from the database using the service function
        files = await list_uploaded_files(db)
        return {"files": files}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@teacher_router.get("/download/{filename}")
async def download_file(filename: str):
    try:
        file_path = os.path.join("uploads", filename)
        if os.path.exists(file_path):
            return FileResponse(
                path=file_path, filename=filename, media_type="application/octet-stream"
            )
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
