from typing import List, Optional

from core.models import Role, User
from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from sqlalchemy.exc import SQLAlchemyError
from .schemas import StudentUpdate
from core.models import Certificates,ProfilePicture

async def list_uploaded_files(db: AsyncSession):
    """
    Fetch the list of files stored in the database.
    """
    result = await db.execute(select(Certificates))
    files = result.scalars().all()

    # Convert files to a serializable format
    return [
        {"id": file.id, "filename": file.filename, "filepath": file.filepath}
        for file in files
    ]
    
async def list_uploaded_picture(db: AsyncSession):
    try:
        result = await db.execute(select(ProfilePicture))
        files = result.scalars().all()
        return [
            {"id": file.id, "filename": file.filename, "filepath": file.filepath}
            for file in files
        ]
    except SQLAlchemyError as e:
        raise e
    
async def get_all_students(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[User]:
    query = select(User).where(User.role == Role.STUDENT).offset(skip).limit(limit)
    users = await db.execute(query)
    return users.scalars().all()


async def get_student_account_by_id(
    student_id: int, db: AsyncSession
) -> Optional[User]:
    query = (
        select(User)
        .where(
            and_(
                User.id == student_id,
                User.is_deleted.is_(False),
                User.role == Role.STUDENT,
            )
        )
        .options(selectinload(User.subjects), selectinload(User.application))
    )
    user = await db.execute(query)
    return user.scalar_one_or_none()


async def update_student_account(
    student_id: int, student_in: StudentUpdate, db: AsyncSession
) -> User:
    student = await get_student_account_by_id(student_id=student_id, db=db)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    for field, value in student_in.model_dump(exclude_unset=True).items():
        setattr(student, field, value)

    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student


async def update_students_batch(
    student_updates: List[StudentUpdate], db: AsyncSession
) -> List[User]:
    updated_students = []
    for update_data in student_updates:
        student = await get_student_account_by_id(student_id=update_data.id, db=db)
        if not student:
            continue  # Optionally raise an exception or log missing students

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(student, field, value)

        db.add(student)
        updated_students.append(student)

    await (
        db.commit()
    )  # Commit all at once, reducing the number of database transactions
    for student in updated_students:
        await db.refresh(
            student
        )  # Optionally refresh each one if you need updated data

    return updated_students


async def reset(student_id: int, student_in: StudentUpdate, db: AsyncSession) -> User:
    student = await get_student_account_by_id(student_id=student_id, db=db)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    for field, value in student_in.model_dump(exclude_unset=True).items():
        setattr(student, field, value)

    db.add(student)
    await db.commit()
    await db.refresh(student)
    return student


async def remove_student_by_id(id: int, db: AsyncSession) -> User:
    student = await get_student_account_by_id(student_id=id, db=db)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.is_deleted = True
    await db.commit()
    await db.refresh(student)
    return student


async def set_student_account_status(db: AsyncSession, id: int) -> User:
    student = await get_student_account_by_id(student_id=id, db=db)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.is_active = not student.is_active
    await db.commit()
    await db.refresh(student)
    return student
