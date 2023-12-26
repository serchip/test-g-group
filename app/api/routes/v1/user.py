from fastapi import APIRouter, HTTPException

from app.api.dependencies.database import AsyncSession
from app.api.errors.run_time import NotFoundException
from app.schemas.request.user import CreateUserInRequest
from app.schemas.response.user import UserGetResponse, UsersListResponse
from app.selects.user import get_all_users_selector, get_user_selector
from app.services.user import create_user_service

router = APIRouter(prefix="/v1/users")


@router.get("/", response_model=UsersListResponse)
async def get_user_list(async_session: AsyncSession):
    async with async_session() as session:
        return UsersListResponse(
            users=[user async for user in get_all_users_selector(session=session)]
        )


@router.get("/{user_id}", response_model=UserGetResponse)
async def get_user(user_id: int, async_session: AsyncSession) -> UserGetResponse:
    try:
        async with async_session() as session:
            return await get_user_selector(session=session, user_id=user_id)
    except NotFoundException as _:
        raise HTTPException(status_code=404) from _


@router.post("/", response_model=UserGetResponse)
async def create_user(async_session: AsyncSession, body: CreateUserInRequest):
    return await create_user_service(async_session=async_session, create_user=body)
