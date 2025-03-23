import logging
from typing import Annotated, List  # noqa: F401

from auth.services import admin_access
from auth.utils import get_current_user
from core.models import User
from database.core import get_async_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from subject.models import Subject  # noqa: F401

from .enums import ApplicationStatus
from .models import Application
from .schemas import ApplicationCreate, ApplicationResponse
from .services import (
    get_application_by_id,
    remove_application_by_id,
    send_application,
    update_application_status,
)

logger = logging.getLogger(__name__)

application_router = APIRouter(prefix="/application", tags=["Applications"])


@application_router.post("/", summary="send an application", operation_id="post_apply")
async def apply(
    current_user: Annotated[User, Depends(get_current_user)],
    application_data: ApplicationCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    application = await send_application(
        user_id=current_user.id, application=application_data, db=db
    )
    if application:
        return application
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="User already has an application or User is not a Student",
    )


@application_router.get(
    "/",
    summary="List applications",
    # response_model=List[ApplicationResponse],
    dependencies=[Depends(admin_access)],
    operation_id="get_applications",
)
async def get_applications(db: Annotated[AsyncSession, Depends(get_async_db)]):
    applications = await db.execute(select(Application))
    applications = applications.scalars().all()

    return applications


@application_router.get(
    "/{application_id}",
    summary="Details application using its ID",
    response_model=ApplicationResponse,
    operation_id="get_application_by_id",
)
async def get_applications_by_id(
    application_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    application = await get_application_by_id(application_id, db)
    return application


@application_router.patch(
    "/approve/{application_id}",
    summary="approve a application using its ID",
    dependencies=[Depends(admin_access)],
    operation_id="patch_approve_application",
)
async def approve_appliacation(
    application_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    approved_application = await update_application_status(
        status=ApplicationStatus.APPROVED, application_id=application_id, db=db
    )
    if approved_application:
        return approved_application
    else:
        return {"detail": "failed to approve application"}


@application_router.patch(
    "/reject/{application_id}",
    summary="reject a application using its ID",
    dependencies=[Depends(admin_access)],
    operation_id="patch_reject_application",
)
async def reject_application(
    application_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    reject_application = await update_application_status(
        status=ApplicationStatus.REJECTED, application_id=application_id, db=db
    )
    if reject_application:
        return reject_application
    else:
        return {"detail": "failed to reject application"}


@application_router.patch(
    "/receive/{application_id}",
    summary="receive a application using its ID",
    dependencies=[Depends(admin_access)],
    operation_id="patch_receive_application",
)
async def receive_application(
    application_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    receive_application = await update_application_status(
        status=ApplicationStatus.RECEIVED, application_id=application_id, db=db
    )
    if receive_application:
        return receive_application
    else:
        return {"detail": "failed to receive application"}


@application_router.patch(
    "/pending/{application_id}",
    summary="pending a application using its ID",
    dependencies=[Depends(admin_access)],
    operation_id="patch_pending_application",
)
async def pending_application(
    application_id: int,
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    pending_application = await update_application_status(
        status=ApplicationStatus.PENDING, application_id=application_id, db=db
    )
    if pending_application:
        return pending_application
    else:
        return {"detail": "failed to pending application"}


@application_router.delete(
    "/delete/{application_id}",
    summary="application a message using its ID",
    dependencies=[Depends(admin_access)],
    operation_id="delete_application_by_id",
)
async def delete_message(
    application_id: int, db: Annotated[AsyncSession, Depends(get_async_db)]
):
    student = await remove_application_by_id(application_id, db)
    return student
