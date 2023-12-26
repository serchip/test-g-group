from dataclasses import dataclass

from app.api.dependencies.database import AsyncSession
from app.api.errors.run_time import NotFoundException, UserNotActiveException
from app.db.repositories.user import user
from app.db.repositories.user_session import user_session
from app.schemas.db.user import UserDB
from app.schemas.db.user_session import UserSessionDB


@dataclass(frozen=True, slots=True, kw_only=True)
class GetUserSession:
    _get_user_session_by_id = user_session.get

    async def __call__(
        self, session: AsyncSession, user_session_id: int
    ) -> UserSessionDB | None:
        user_data = await self._get_user_session_by_id(
            session=session, user_session_id=user_session_id
        )
        if not user_data:
            return None
        return UserSessionDB.from_orm(user_data)


get_user_session_selector = GetUserSession()


@dataclass(frozen=True, slots=True, kw_only=True)
class GetUsersByToken:
    _get_user_by_email = user.get_by_email
    _get_user_session = user_session.get_by_user

    async def __call__(
        self, session: AsyncSession, username: str, access_token: str
    ) -> UserDB | None:
        user_data = await self._get_user_by_email(session=session, email=username)
        if not user_data:
            raise NotFoundException
        user_session = await self._get_user_session(
            session=session, user_id=user_data.id
        )
        if not user_session or user_session.access_token != access_token:
            raise UserNotActiveException
        return UserDB.from_orm(user_data)


get_user_by_token_selector = GetUsersByToken()
