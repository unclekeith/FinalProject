from datetime import datetime, timedelta

from core.config import settings
from core.enums import Role
from core.models import User
from core.schemas import UserCreate
from fastapi import Depends, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.schemas import UserPasswordUpdate
from .schemas import TokenResponse
from .utils import (
    generate_access_token,
    generate_password_hash,
    get_current_user,
    verify_password_hash,
)


async def create_user_account(user_in: UserCreate, db_session: AsyncSession):
    query = select(User).where(User.email == user_in.email)
    result = await db_session.execute(query)
    user = result.scalar_one_or_none()

    if user:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email already registered",
        )

    hashed_password = await generate_password_hash(user_in.password)
    new_user = User(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        email=user_in.email.lower(),
        password=hashed_password,
        is_active=True,  # or False if you want to verify first
        is_verified=True,  # or False if you want to verify first
        updated_at=datetime.now(),
        role=Role.STUDENT,  # Default role
    )

    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    return new_user


async def create_access_token(
    user_in: OAuth2PasswordRequestForm, db_session: AsyncSession
):
    query = select(User).where(User.email == user_in.username)
    result = await db_session.execute(query)
    user = result.scalar_one_or_none()

    if not user or not await verify_password_hash(user_in.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    await _verify_user_access(user=user)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await generate_access_token(
        data={"id": user.id}, expires=access_token_expires
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=access_token_expires.seconds,
    )


async def _verify_user_access(user: User):
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your account is inactive. Please contact support",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your account is not verified. We have sent the verification email",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_login_response(access_token: str):
    response = RedirectResponse(url="/me", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        # secure=True,
        samesite="Lax",
    )
    return response


async def admin_access(
    request: Request, current_user: User = Depends(get_current_user)
):
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this [ADMIN] Resource",
        )

    return current_user


async def password_reset(email: str, updated_password: UserPasswordUpdate, db: AsyncSession):
    """
    Resets the password for a given user by email.
    Args:
        email (str): The email of the user whose password is being reset.
        updated_password (UserPasswordUpdate): Contains the new password.
        db (AsyncSession): The database session.
    """
    # Fetch the user by email
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()

    if not user:
        return None
    try:
        # Hash the password (await if the function is async)
        hashed_password = await generate_password_hash(updated_password.new_password)  # Await the coroutine

        # Update the user's password
        user.password = hashed_password
        db.add(user)
        await db.commit()
        await db.refresh(user)  # Refresh to get updated data if needed
    except Exception as e:
        # If any error occurs, raise a HTTP exception
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating the password: {str(e)}"
        )

    return user