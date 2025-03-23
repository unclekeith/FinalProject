from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Subject
from .schemas import SubjectCreate, SubjectUpdate


async def create_subject(subject_in: SubjectCreate, db: AsyncSession):
    subject_exists = await get_subject_by_name(db=db, subject_name=subject_in.name)

    if subject_exists is not None:
        raise HTTPException(status_code=400, detail="Subject already exists")

    new_subject = Subject(**subject_in.model_dump())
    db.add(new_subject)
    await db.commit()
    await db.refresh(new_subject)

    return new_subject


async def get_all_subjects(db: AsyncSession):
    query = select(Subject).where(Subject.is_deleted.is_(False))
    result = await db.execute(query)
    subjects = result.scalars().all()
    return subjects


async def update_subject(db: AsyncSession, subject_id: int, subject: SubjectUpdate):
    existing_subject = await get_subject_by_id(db=db, subject_id=subject_id)

    if existing_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Update fields
    for field, value in subject.model_dump(exclude_unset=True).items():
        setattr(existing_subject, field, value)

    db.add(existing_subject)
    await db.commit()
    await db.refresh(existing_subject)

    return existing_subject


async def get_subject_by_id(db: AsyncSession, subject_id: int):
    query = select(Subject).where(
        and_(Subject.id == subject_id, Subject.is_deleted.is_(False))
    )
    result = await db.execute(query)
    subject = result.unique().scalar_one_or_none()

    return subject


async def get_subject_by_name(db: AsyncSession, subject_name: str):
    query = select(Subject).where(
        and_(Subject.name == subject_name, Subject.is_deleted.is_(False))
    )
    result = await db.execute(query)
    subject = result.unique().scalar_one_or_none()

    return subject
