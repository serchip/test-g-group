from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

import jwt

from app.core.config import settings
from app.schemas.request.token import Token
from app.schemas.response.auth import AuthTokenResponse, AuthTokensResponse


@dataclass(frozen=True, slots=True, kw_only=True)
class JWTService:
    jwt_secret_key: str = settings.SECRET_KEY
    jwt_algorithms: tuple[str] = tuple([settings.ALGORITHM])
    access_token_exp_delta: timedelta = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token_exp_delta: timedelta = timedelta(days=16)
    jwt_not_before_gap: timedelta = timedelta(minutes=1)
    jwt_token_refresh_until: timedelta = timedelta(days=3)

    def token_expires_soon(self, expires_at: datetime, when: datetime) -> bool:
        expires_in = expires_at - when
        return expires_in < self.jwt_token_refresh_until

    def generate_token(
        self,
        user_id: int,
        when: datetime,
        email: str,
        exp_delta: timedelta,
    ) -> Token:
        return Token(
            exp=when + exp_delta,
            nbf=when - self.jwt_not_before_gap,
            iat=when,
            aud=[],
            sub=user_id,
            email=email,
        )

    def generate_access_token(
        self,
        user_id: int,
        when: datetime,
        email: str,
    ) -> Token:
        return self.generate_token(
            exp_delta=self.access_token_exp_delta,
            when=when,
            user_id=user_id,
            email=email,
        )

    def generate_refresh_token(
        self,
        user_id: int,
        when: datetime,
        email: str,
    ) -> Token:
        return self.generate_token(
            exp_delta=self.refresh_token_exp_delta,
            when=when,
            user_id=user_id,
            email=email,
        )

    def generate_tokens_pair(
        self,
        user_id: int,
        when: datetime,
        email: str,
    ) -> AuthTokensResponse:
        access_token = self.generate_access_token(
            user_id=user_id,
            when=when,
            email=email,
        )
        refresh_token = self.generate_refresh_token(
            user_id=user_id,
            when=when,
            email=email,
        )
        return AuthTokensResponse(
            access=AuthTokenResponse(
                token=self.encode_token(access_token),
                expires_at=access_token.exp,
            ),
            refresh=AuthTokenResponse(
                token=self.encode_payload(
                    {
                        "sub": str(refresh_token.sub),
                        **refresh_token.dict(include={"exp", "nbf", "iat", "aud"}),
                    }
                ),
                expires_at=refresh_token.exp,
            ),
        )

    def encode_token(self, token: Token) -> str:
        payload = token.dict(exclude={"sub"})
        return self.encode_payload(payload={**payload, "sub": str(token.sub)})

    def encode_payload(self, payload: dict[str, Any]) -> str:
        return jwt.encode(
            payload=payload,
            key=self.jwt_secret_key,
        )

    def decode_token(self, token: str):
        username = None
        expire_time = None

        try:
            payload = jwt.decode(
                jwt=token,
                key=self.jwt_secret_key,
                algorithms=self.jwt_algorithms,
            )
            username: Optional[str] = payload.get("email")
            expire_time: Optional[datetime] = payload.get("exp")

        except jwt.exceptions.InvalidTokenError:
            raise
        return username, expire_time


jwt_service = JWTService()
