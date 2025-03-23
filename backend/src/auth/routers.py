from typing import Annotated

from core.schemas import UserCreate
from database.core import get_async_db
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from .services import (
    create_login_response,
    create_user_account,
)
from .utils import generate_access_token, get_user, verify_password_hash

# Create the router
auth_router = APIRouter(tags=["Auth"])


# Register new user
@auth_router.post("/register", name="register", operation_id="post_register")
async def register_user(
    user: Annotated[UserCreate, Form()],
    db_session: Annotated[AsyncSession, Depends(get_async_db)],
):
    # Create a UserCreate instance manually from form data
    user = UserCreate(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=user.password,
        phone_number=user.phone_number,
    )

    user = await create_user_account(user_in=user, db_session=db_session)
    db_session.add(user)
    await db_session.commit()

    # Generate access token
    access_token = await generate_access_token(data={"sub": user.email})

    # Create a response with the access token
    return create_login_response(access_token)


# Login the user
@auth_router.post(
    "/login", response_class=HTMLResponse, name="login", operation_id="post_login"
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db_session: Annotated[AsyncSession, Depends(get_async_db)],
):
    user = await get_user(db_session=db_session, username=form_data.username)

    if not user or not await verify_password_hash(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await generate_access_token(data={"sub": user.email})
    return create_login_response(access_token)


# logout the user
@auth_router.post("/logout", name="logout", operation_id="post_logout")
async def logout_user(request: Request):
    # Create a response with a JSON body indicating logout success
    response = JSONResponse(
        content={"detail": "Logout successful, please log in again."},
        status_code=status.HTTP_200_OK,
    )

    # Clear the cookie by setting an expiration date in the past
    response.set_cookie(
        key="access_token",
        value="",
        expires="Thu, 01 Jan 1970 00:00:00 GMT",
        httponly=True,
        secure=True,
        samesite="Lax",
    )

    return response
