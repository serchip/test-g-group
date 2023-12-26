from dataclasses import dataclass
from datetime import datetime

from app.api.dependencies.database import AsyncSession
from app.commands.user import create_user_command, create_user_session_command
from app.schemas.db.user import UserDB
from app.schemas.db.user_session import UserSessionDB
from app.schemas.request.user import CreateUserInRequest
from app.selects.user import get_user_selector
from app.selects.user_session import get_user_session_selector
from app.services.password import generate_hashed_pair


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserService:
    _create_user = create_user_command
    _get_user = get_user_selector
    _generate_hashed_pair = generate_hashed_pair

    def _get_hashed_salt_password(self, password: str = "12345"):
        # Генерируем или получаем из запроса пароль
        hashed_password, salt = generate_hashed_pair(password=password)
        return salt + hashed_password

    async def __call__(
        self, async_session: AsyncSession, create_user: CreateUserInRequest
    ) -> UserDB:
        async with async_session() as session:
            user_id = await self._create_user(
                session=session,
                email=create_user.email,
                first_name=create_user.first_name,
                last_name=create_user.last_name,
                hashed_password=self._get_hashed_salt_password(create_user.password),
            )
            if not user_id:
                raise ValueError()  # TODO: Валидацию по почте до создания
            user_data = await get_user_selector(session=session, user_id=user_id)
            await session.commit()
            # Добавить отправку почты
            return user_data


create_user_service = CreateUserService()


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserSessionService:
    _create_user_session = create_user_session_command

    async def __call__(
        self, session: AsyncSession, user_id: int, token: str, expires_at: datetime
    ) -> UserSessionDB:
        user_session_id = await self._create_user_session(
            session=session, user_id=user_id, token=token, expires_at=expires_at
        )
        if not user_id:
            raise ValueError()
        user_data = await get_user_session_selector(
            session=session, user_session_id=user_session_id
        )
        await session.commit()
        return user_data


create_user_session_service = CreateUserSessionService()
