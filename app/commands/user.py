from dataclasses import dataclass
from datetime import datetime

from app.api.dependencies.database import AsyncSession
from app.db.repositories.user import user
from app.db.repositories.user_session import user_session


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserCommand:
    _create_user = user.create

    async def __call__(
        self,
        session: AsyncSession,
        email: str,
        first_name: str,
        last_name: str,
        hashed_password: bytes,
    ) -> int | None:
        return await self._create_user(
            session=session,
            email=email,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hashed_password,
        )


create_user_command = CreateUserCommand()


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserSessionCommand:
    _create_user_session = user_session.create

    async def __call__(
        self, session: AsyncSession, user_id: int, token: str, expires_at: datetime
    ) -> int | None:
        return await self._create_user_session(
            session=session,
            user_id=user_id,
            token=token,
            expires_at=expires_at,
        )


create_user_session_command = CreateUserSessionCommand()


@dataclass(frozen=True, slots=True, kw_only=True)
class DeleteUserSessionCommand:
    _delete_user_session = user_session.delete_session

    async def __call__(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> int | None:
        return await self._delete_user_session(
            session=session,
            user_id=user_id,
        )


delete_user_session_command = DeleteUserSessionCommand()
