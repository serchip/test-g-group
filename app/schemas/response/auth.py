from datetime import datetime

from pydantic import BaseModel

from app.schemas.response.user import UserGetResponse


class AuthTokenResponse(BaseModel):
    token: str
    expires_at: datetime


class AuthTokensResponse(BaseModel):
    access: AuthTokenResponse
    refresh: AuthTokenResponse


class AuthResponse(BaseModel):
    user: UserGetResponse
    tokens: AuthTokensResponse


class LoginTokenResponse(BaseModel):
    access_token: str
    token_type: str
