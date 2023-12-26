from dataclasses import dataclass

from app.api.dependencies.database import AsyncSession
from app.db.repositories.post import post


@dataclass(frozen=True, slots=True, kw_only=True)
class CreatePostCommand:
    _create_row = post.create

    async def __call__(
        self,
        session: AsyncSession,
        title: str,
        user_id: int,
        description: str | None = None,
    ) -> int | None:
        return await self._create_row(
            session=session,
            title=title,
            user_id=user_id,
            description=description,
        )


create_post_command = CreatePostCommand()


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdatePostCommand:
    _update_row = post.update

    async def __call__(
        self,
        session: AsyncSession,
        post_id: int,
        title: str,
        user_id: int,
        description: str | None = None,
    ) -> int | None:
        return await self._update_row(
            session=session,
            post_id=post_id,
            title=title,
            user_id=user_id,
            description=description,
        )


update_post_command = UpdatePostCommand()


@dataclass(frozen=True, slots=True, kw_only=True)
class DeletePostCommand:
    _delete_row = post.delete

    async def __call__(
        self, session: AsyncSession, post_id: int, user_id: int
    ) -> int | None:
        return await self._delete_row(session=session, post_id=post_id, user_id=user_id)


delete_post_command = DeletePostCommand()
