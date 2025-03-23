import datetime
from typing import List, Optional

from core.models import Role, User
from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from teacher.models import Conversation, Messages
from teacher.schemas import MessageCreate

from .models import File
from .schemas import TeacherUpdate


async def get_all_conversations(db: AsyncSession):
    result = await db.execute(
        select(Conversation).options(joinedload(Conversation.teacher))
    )
    return result.scalars().all()


async def get_chat_history(db: AsyncSession, teacher_id: int):
    result = await db.execute(
        select(Messages).where(Messages.teacher_id == teacher_id).order_by(Messages.id)
    )
    return result.scalars().all()


async def save_message(db: AsyncSession, message_data: MessageCreate):
    message = Messages(
        teacher_id=message_data.teacher_id,
        sender=message_data.sender,
        content=message_data.content,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def list_uploaded_files(db: AsyncSession):
    """
    Fetch the list of files stored in the database.
    """
    result = await db.execute(select(File))
    files = result.scalars().all()

    # Convert files to a serializable format
    return [
        {"id": file.id, "filename": file.filename, "filepath": file.filepath}
        for file in files
    ]


async def get_replies(db: AsyncSession, teacher_id: int):
    result = await db.execute(
        select(Messages)
        .where(Messages.teacher_id == teacher_id, Messages.sender == "admin")
        .order_by(Messages.id)
    )
    return result.scalars().all()


async def get_all_teachers(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[User]:
    query = select(User).where(User.role == Role.TEACHER).offset(skip).limit(limit)
    users = await db.execute(query)
    return users.scalars().all()


async def get_teacher_account_by_id(
    teacher_id: int, db: AsyncSession
) -> Optional[User]:
    query = select(User).where(
        and_(
            User.id == teacher_id,
            User.is_deleted.is_(False),
            User.role == Role.TEACHER,
        )
    )
    user = await db.execute(query)
    return user.scalar_one_or_none()


async def update_teacher_account(
    teacher_id: int, teacher_in: TeacherUpdate, db: AsyncSession
) -> User:
    teacher = await get_teacher_account_by_id(teacher_id=teacher_id, db=db)

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    for field, value in teacher_in.model_dump(exclude_unset=True).items():
        setattr(teacher, field, value)

    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)
    return teacher


async def update_teacher_batch(
    teacher_updates: List[TeacherUpdate], db: AsyncSession
) -> List[User]:
    updated_teachers = []
    for update_data in teacher_updates:
        teacher = await get_teacher_account_by_id(teacher_id=update_data.id, db=db)
        if not teacher:
            continue  # Skip if teacher not found

        # Update only fields with new values
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(teacher, field, value)

        db.add(teacher)
        updated_teachers.append(teacher)

    await db.commit()  # Commit all updates at once
    for teacher in updated_teachers:
        await db.refresh(teacher)  # Refresh to get updated data

    return updated_teachers


async def reset(teacher_id: int, teacher_in: TeacherUpdate, db: AsyncSession) -> User:
    teacher = await get_teacher_account_by_id(teacher_id=teacher_id, db=db)

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    for field, value in teacher_in.model_dump(exclude_unset=True).items():
        setattr(teacher, field, value)

    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)
    return teacher


async def remove_teacher_by_id(id: int, db: AsyncSession) -> User:
    teacher = await get_teacher_account_by_id(teacher_id=id, db=db)

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    teacher.is_deleted = True
    await db.commit()
    await db.refresh(teacher)
    return teacher


async def set_teacher_account_status(db: AsyncSession, id: int) -> User:
    teacher = await get_teacher_account_by_id(teacher_id=id, db=db)

    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    teacher.is_active = not teacher.is_active
    await db.commit()
    await db.refresh(teacher)
    return teacher


async def check_out_teacher(teacher_id: int, db: AsyncSession) -> bool:
    teacher = await get_teacher_account_by_id(teacher_id=teacher_id, db=db)
    if not teacher:
        return False  # Could raise an exception if preferable

    teacher.is_checked_out = True
    teacher.last_checked_out = (
        datetime.datetime.utcnow()
    )  # Corrected: use datetime.datetime.utcnow()

    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)
    return True


async def check_in_teacher(teacher_id: int, db: AsyncSession):
    # Fetch the teacher account by ID
    teacher = await get_teacher_account_by_id(teacher_id=teacher_id, db=db)

    # If the teacher is not found, raise a 404 error
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found.")

    # Update the teacher's status
    teacher.is_checked_out = False  # Set to false to indicate the teacher is checked in
    teacher.last_checked_in = (
        datetime.datetime.utcnow()
    )  # Corrected: use datetime.datetime.utcnow()
    # Add the updated teacher back to the session and commit the changes
    db.add(teacher)
    await db.commit()
    await db.refresh(teacher)

    return True
