from dataclasses import dataclass
from typing import AsyncIterator

from app.api.dependencies.database import AsyncSession
from app.api.errors.run_time import NotFoundException
from app.db.repositories.user import user
from app.schemas.db.user import UserDB


@dataclass(frozen=True, slots=True, kw_only=True)
class GetAllUsers:
    _get_user_list = user.list

    async def __call__(self, session: AsyncSession) -> AsyncIterator[UserDB]:
        async for user_data in self._get_user_list(session=session):
            yield UserDB.from_orm(user_data)


get_all_users_selector = GetAllUsers()


@dataclass(frozen=True, slots=True, kw_only=True)
class GetUsers:
    _get_user = user.get

    async def __call__(self, session: AsyncSession, user_id: int) -> UserDB | None:
        user_data = await self._get_user(session=session, user_id=user_id)
        if not user_data:
            raise NotFoundException()
        # TODO: add if none
        return UserDB.from_orm(user_data)


get_user_selector = GetUsers()


@dataclass(frozen=True, slots=True, kw_only=True)
class GetUsersByEmail:
    _get_user_by_email = user.get_by_email

    async def _get_user_data(self, session: AsyncSession, email):
        user_data = await self._get_user_by_email(session=session, email=email)
        if not user_data:
            return None
        return user_data

    async def __call__(self, session: AsyncSession, email: str) -> UserDB | None:
        user_data = await self._get_user_data(session=session, email=email)
        if not user_data:
            return None
        return UserDB.from_orm(user_data)


get_user_by_email_selector = GetUsersByEmail()
