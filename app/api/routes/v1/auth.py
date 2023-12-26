from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth import access_control
from app.api.dependencies.database import AsyncSession
from app.api.errors.run_time import NotFoundException
from app.schemas.db.user import UserDB
from app.schemas.response.auth import LoginTokenResponse
from app.schemas.response.user import UserGetResponse
from app.services.auth import auth_logout_user_service, auth_user_service

router = APIRouter(prefix="/v1/auth")


@router.post("/login", response_model=LoginTokenResponse)
async def email_login(
    async_session: AsyncSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> LoginTokenResponse:
    try:
        async with async_session() as session:
            auth_response = await auth_user_service(
                session=session, form_data=form_data
            )
            return {
                "access_token": auth_response.tokens.access.token,
                "token_type": "bearer",
            }
    except NotFoundException:
        raise HTTPException(status_code=404)
    except ValueError:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)


@router.put("/logout")
async def logout(
    async_session: AsyncSession,
    current_user: Annotated[UserDB, Depends(access_control)],
) -> None:
    try:
        async with async_session() as session:
            return await auth_logout_user_service(
                session=session, user_id=current_user.id
            )
    except NotFoundException:
        raise HTTPException(status_code=404)
    except ValueError:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/curent_user", response_model=UserGetResponse)
async def curent_user(
    async_session: AsyncSession,
    current_user: Annotated[UserDB, Depends(access_control)],
) -> UserGetResponse:
    try:
        return current_user
    except NotFoundException:
        raise HTTPException(status_code=404)
    except ValueError:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
