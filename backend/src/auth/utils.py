from datetime import datetime, timedelta

import jwt
from core.config import settings
from core.enums import Role
from core.models import User
from database.core import get_async_db
from fastapi import Cookie, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def generate_password_hash(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


async def verify_password_hash(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def generate_access_token(
    *, data: dict, expires: timedelta = timedelta(minutes=15)
):
    payload = data.copy()
    expires_in = datetime.utcnow() + expires
    payload.update({"exp": expires_in})

    return jwt.encode(
        payload=payload,
        key=settings.JWT_ACCESS_SECRET_KEY,
        algorithm=settings.ENCRYPTION_ALGORITHM,
    )


async def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_ACCESS_SECRET_KEY,
            algorithms=[settings.ENCRYPTION_ALGORITHM],
        )
    except PyJWTError:
        return None

    return payload


# User related stuff
async def get_user(db_session: AsyncSession, username: str):
    query = (
        select(User)
        .filter(User.email == username)
        .options(selectinload(User.subjects), selectinload(User.application))
    )
    result = await db_session.execute(query)
    return result.unique().scalar_one_or_none()


async def get_current_user(
    db_session: AsyncSession = Depends(get_async_db), access_token: str = Cookie(None)
):
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = access_token.split(" ")[1] if " " in access_token else access_token

        payload = jwt.decode(
            token,
            settings.JWT_ACCESS_SECRET_KEY,
            algorithms=[settings.ENCRYPTION_ALGORITHM],
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = await get_user(db_session, username)
        if user is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token has expired"},
        )

    return user


def role_required(required_role: Role):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return role_checker
