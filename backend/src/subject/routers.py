import logging
from typing import Annotated, List

from auth.services import admin_access
from auth.utils import get_current_user
from core.models import User
from database.core import get_async_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .models import Subject
from .schemas import SubjectCreate, SubjectResponse, SubjectsCreate, SubjectUpdate
from .services import create_subject, get_all_subjects, update_subject

logger = logging.getLogger(__name__)

subject_router = APIRouter(prefix="/subjects", tags=["Subjects"])


@subject_router.get(
    "/list",
    summary="List all subjects",
    response_model=List[SubjectResponse],
    dependencies=[Depends(get_current_user)],
    operation_id="get_subjects",
)
async def list_subjects(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> List[Subject]:
    """A student is only able to list their own subjects"""
    subjects = await get_all_subjects(db=db)
    logger.info(f"User {current_user.id} requested their subjects.")
    return subjects


@subject_router.post(
    "/add_one",
    summary="Add one subject at a time",
    response_model=SubjectResponse,
    dependencies=[Depends(admin_access)],
    operation_id="post_add_subject",
)
async def add_subject(
    current_user: Annotated[User, Depends(get_current_user)],
    subject: SubjectCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> Subject:
    result = await create_subject(subject_in=subject, db=db)
    return result


@subject_router.post(
    "/add_many",
    summary="Add multiple subjects at a time",
    response_model=List[SubjectResponse],
    dependencies=[Depends(admin_access)],
    operation_id="post_bulk_add_subject",
)
async def add_subjects(
    current_user: Annotated[User, Depends(get_current_user)],
    subjects: SubjectsCreate,  # Expecting SubjectsCreate model with list of subjects
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> List[SubjectResponse]:
    results = []
    for subject in subjects.subjects:
        _result = await create_subject(subject_in=subject, db=db)
        results.append(_result)
        logger.info(f"User {current_user.id} added subject {_result.name}.")
    return results


@subject_router.patch(
    "/update/{subject_id}",
    summary="Update a subject using its ID",
    response_model=SubjectResponse,
    dependencies=[Depends(admin_access)],
    operation_id="patch_update_subject_by_id",
)
async def post_update_subject(
    subject_id: int,
    subject: SubjectUpdate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> Subject:
    updated_subject = await update_subject(
        db=db, subject_id=subject_id, subject=subject
    )

    return updated_subject


@subject_router.delete(
    "/delete/{subject_id}",
    summary="Delete a subject using its ID",
    dependencies=[Depends(admin_access)],
    operation_id="delete_subject_by_id",
)
async def delete_subject(
    subject_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
) -> SubjectResponse:
    query = select(Subject).filter(Subject.id == subject_id)
    result = await db.execute(query)
    deleted_subject = result.unique().scalar_one_or_none()

    if deleted_subject is None:
        raise HTTPException(status_code=404, detail="Subject not found")

    deleted_subject.is_deleted = True
    await db.commit()
    return deleted_subject
