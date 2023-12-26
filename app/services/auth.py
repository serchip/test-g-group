from dataclasses import dataclass
from datetime import datetime

from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.database import AsyncSession
from app.api.errors.run_time import NotFoundException, UserNotActiveException
from app.commands.user import delete_user_session_command
from app.schemas.db.user import UserDB
from app.schemas.response.auth import AuthResponse
from app.selects.user import get_user_by_email_selector
from app.selects.user_session import get_user_by_token_selector
from app.services.jwt import jwt_service
from app.services.password import hash_password
from app.services.user import create_user_session_service


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthUserService:
    _get_user_by_email = get_user_by_email_selector
    _jwt_service = jwt_service
    _create_user_session = create_user_session_service
    _delete_user_session = delete_user_session_command

    async def __call__(
        self, session: AsyncSession, form_data: OAuth2PasswordRequestForm
    ):
        user_data = await self._get_user_by_email(
            session=session, email=form_data.username
        )
        if not user_data:
            raise ValueError()  # Использовать кастомную
        if not self._check_password(
            password=form_data.password,
            salt=user_data.hashed_password[:32],
            hashed_password=user_data.hashed_password[32:],
        ):
            raise ValueError()  # Использовать кастомную

        when = datetime.utcnow()
        tokens = self._jwt_service.generate_tokens_pair(
            user_id=user_data.id,
            email=user_data.email,
            when=when,
        )
        await self._delete_user_session(session=session, user_id=user_data.id)
        await self._create_user_session(
            session=session,
            user_id=user_data.id,
            token=tokens.access.token,
            expires_at=tokens.access.expires_at,
        )
        return AuthResponse(user=user_data, tokens=tokens)

    @staticmethod
    def _check_password(password: str, salt: bytes, hashed_password: bytes) -> bool:
        return hash_password(password, salt) == hashed_password


auth_user_service = AuthUserService()


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthCheckAccessTokenService:
    _jwt_service = jwt_service
    _get_user_by_token = get_user_by_token_selector

    async def __call__(
        self, session: AsyncSession, access_token: str | None = None
    ) -> UserDB | None:
        username, expire_time = self._jwt_service.decode_token(access_token)
        if username and expire_time and access_token:
            if expire_time > int(datetime.utcnow().timestamp()):
                try:
                    user = await self._get_user_by_token(
                        session=session, username=username, access_token=access_token
                    )
                    if user and user.is_active:
                        return user
                    else:
                        raise UserNotActiveException
                except NotFoundException:
                    return None
        return None


auth_check_access_token = AuthCheckAccessTokenService()


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthLogoutUserService:
    _logout_user = delete_user_session_command

    async def __call__(self, session: AsyncSession, user_id: str | None = None):
        await self._logout_user(session=session, user_id=user_id)
        return None


auth_logout_user_service = AuthLogoutUserService()
