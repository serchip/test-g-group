from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.api.dependencies.database import AsyncSession
from app.core.config import settings
from app.schemas.db.user import UserDB
from app.services.auth import auth_check_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)


async def access_control(
    request: Request, async_session: AsyncSession, token: str = Depends(oauth2_scheme)
) -> UserDB | None:
    async with async_session() as session:
        user = await auth_check_access_token(session=session, access_token=token)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
    # perm = f"{request.scope['route'].name}.{request.scope['endpoint'].__name__}"
    # if not (user.is_active and (user.is_staff or perm in user.get_user_permissions())):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Not enough permissions",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
