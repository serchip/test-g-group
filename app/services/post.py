from dataclasses import dataclass

from app.api.dependencies.database import AsyncSession
from app.commands.post import create_post_command, update_post_command
from app.schemas.db.post import PostDB
from app.schemas.request.post import CreatePostInRequest
from app.selects.post import get_post_selector


@dataclass(frozen=True, slots=True, kw_only=True)
class CreatePostService:
    _create_row = create_post_command
    _get_row = get_post_selector

    async def __call__(
        self,
        async_session: AsyncSession,
        create_post: CreatePostInRequest,
        user_id: int,
    ) -> PostDB:
        async with async_session() as session:
            if not user_id:
                raise ValueError()
            row_id = await self._create_row(
                session=session,
                title=create_post.title,
                description=create_post.description,
                user_id=user_id,
            )
            return await self._get_row(session=session, user_id=user_id, post_id=row_id)


create_post_service = CreatePostService()


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdatePostService:
    _update_row = update_post_command
    _get_row = get_post_selector

    async def __call__(
        self,
        async_session: AsyncSession,
        update_data: CreatePostInRequest,
        user_id: int,
        post_id: int,
    ) -> PostDB:
        async with async_session() as session:
            if not user_id:
                raise ValueError()
            await self._get_row(session=session, post_id=post_id, user_id=user_id)
            await self._update_row(
                session=session,
                title=update_data.title,
                description=update_data.description,
                user_id=user_id,
                post_id=post_id,
            )
            return await self._get_row(
                session=session, post_id=post_id, user_id=user_id
            )


update_post_service = UpdatePostService()
