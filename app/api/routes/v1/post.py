from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies.auth import access_control
from app.api.dependencies.database import AsyncSession
from app.api.errors.run_time import NotFoundException
from app.commands.post import delete_post_command
from app.schemas.db.post import PostDB
from app.schemas.request.post import CreatePostInRequest
from app.schemas.response.post import PostGetResponse, PostsListResponse
from app.services.post import create_post_service, update_post_service

from app.selects.post import (  # isort: skip
    get_all_post_selector,
    get_count_post_selector,
    get_post_selector,
)

router = APIRouter(prefix="/v1/posts")


@router.get("/", response_model=PostsListResponse)
async def get_post_list(
    async_session: AsyncSession,
    current_user: Annotated[PostDB, Depends(access_control)],
    limit: int = 10,
    offset: int = 0,
):
    async with async_session() as session:
        return PostsListResponse(
            posts=[
                post
                async for post in get_all_post_selector(
                    session=session, user_id=current_user.id, limit=limit, offset=offset
                )
            ],
            total=await get_count_post_selector(
                session=session, user_id=current_user.id
            ),
        )


@router.get("/{post_id}", response_model=PostGetResponse)
async def get_post(
    post_id: int,
    async_session: AsyncSession,
    current_user: Annotated[PostDB, Depends(access_control)],
) -> PostGetResponse:
    try:
        async with async_session() as session:
            return await get_post_selector(
                session=session, user_id=current_user.id, post_id=post_id
            )
    except NotFoundException as _:
        raise HTTPException(status_code=404) from _


@router.patch("/{post_id}", response_model=PostGetResponse)
async def update_post(
    async_session: AsyncSession,
    body: CreatePostInRequest,
    post_id: int,
    current_user: Annotated[PostDB, Depends(access_control)],
):
    try:
        return await update_post_service(
            async_session=async_session,
            update_data=body,
            post_id=post_id,
            user_id=current_user.id,
        )
    except NotFoundException as _:
        raise HTTPException(status_code=404) from _


@router.post("/", response_model=PostGetResponse)
async def create_post(
    async_session: AsyncSession,
    body: CreatePostInRequest,
    current_user: Annotated[PostDB, Depends(access_control)],
):
    return await create_post_service(
        async_session=async_session, create_post=body, user_id=current_user.id
    )


@router.delete("/{post_id}")
async def delete_post(
    async_session: AsyncSession,
    post_id: int,
    current_user: Annotated[PostDB, Depends(access_control)],
):
    try:
        async with async_session() as session:
            post = await get_post_selector(
                session=session, user_id=current_user.id, post_id=post_id
            )
            return await delete_post_command(
                session=session, post_id=post.id, user_id=current_user.id
            )
    except NotFoundException as _:
        raise HTTPException(status_code=404) from _
