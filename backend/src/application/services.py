from typing import List, Optional

from core.enums import Role
from core.models import User
from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from subject.models import Subject

from .models import Application, ApplicationStatus
from .schemas import ApplicationCreate, ApplicationUpdate


async def get_all_applications(db: AsyncSession) -> Optional[List[Application]]:
    query = select(Application).where(Application.is_deleted.is_(False))
    applications = await db.execute(query)
    return applications.scalars().all()


async def get_application_by_id(
    application_id: int, db: AsyncSession
) -> Optional[Application]:
    query = (
        select(Application)
        .where(Application.id == application_id)
        .options(selectinload(Application.subjects))
    )
    result = await db.execute(query)
    return result.unique().scalar_one_or_none()


async def send_application(
    user_id: int, application: ApplicationCreate, db: AsyncSession
):
    # Query to check if the user is active and a student
    query = select(User).where(
        and_(
            User.id == user_id,
            User.is_active.is_(True),
            User.role == Role.STUDENT,
        )
    )
    result = await db.execute(query)
    user = result.unique().scalar_one_or_none()

    if user is None:
        return None

    # Check for existing applications
    application_query = select(Application).where(Application.applicant_id == user_id)
    existing_application = await db.execute(application_query)

    if existing_application.unique().scalar_one_or_none():
        return None

    # Create a new application instance
    new_application = Application(applicant_id=user_id)

    if application.subject_ids:
        # Fetch subjects with the provided IDs
        subject_query = select(Subject).where(Subject.id.in_(application.subject_ids))
        subject_results = await db.execute(subject_query)
        subjects = subject_results.scalars().all()
        if not subjects:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more subjects not found",
            )

        # Associate the fetched subjects with the application
        new_application.subjects.extend(subjects)

    # Add and commit the new application
    db.add(new_application)
    await db.commit()
    await db.refresh(new_application)

    return new_application


async def update_application(
    application_id: int, application_in: ApplicationUpdate, db: AsyncSession
) -> Optional[Application]:
    application = await get_application_by_id(application_id=application_id, db=db)

    if application is None:
        return None

    for field, value in application_in.model_dump(exclude_unset=True).items():
        setattr(application, field, value)

    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


async def update_application_status(
    application_id: int, status: ApplicationStatus, db: AsyncSession
) -> Optional[Application]:
    application = await get_application_by_id(application_id=application_id, db=db)

    if application is None:
        return None

    application.status = status
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


async def remove_application_by_id(
    application_id: int, db: AsyncSession
) -> Optional[Application]:
    application = await get_application_by_id(application_id=application_id, db=db)

    if application is None:
        return None

    application.is_deleted = True
    await db.commit()
    await db.refresh(application)
    return application
