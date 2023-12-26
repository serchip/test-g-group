from dataclasses import dataclass
from typing import AsyncIterator

from app.api.dependencies.database import AsyncSession
from app.api.errors.run_time import NotFoundException
from app.db.repositories.post import post
from app.schemas.db.post import PostDB


@dataclass(frozen=True, slots=True, kw_only=True)
class GetAllPosts:
    _get_list = post.list

    async def __call__(
        self, session: AsyncSession, limit: int, offset: int, user_id: int
    ) -> AsyncIterator[PostDB]:
        async for row_data in self._get_list(
            session=session, limit=limit, offset=offset, user_id=user_id
        ):
            yield PostDB.from_orm(row_data)


get_all_post_selector = GetAllPosts()


@dataclass(frozen=True, slots=True, kw_only=True)
class GetCountPost:
    _get_row = post.count

    async def __call__(self, session: AsyncSession, user_id: int) -> int:
        row_data = await self._get_row(session=session, user_id=user_id)
        return int(row_data) | 0


get_count_post_selector = GetCountPost()


@dataclass(frozen=True, slots=True, kw_only=True)
class GetPost:
    _get_row = post.get

    async def __call__(
        self, session: AsyncSession, post_id: int, user_id: int
    ) -> PostDB | None:
        row_data = await self._get_row(
            session=session, post_id=post_id, user_id=user_id
        )
        if not row_data:
            raise NotFoundException()
        return PostDB.from_orm(row_data)


get_post_selector = GetPost()
