from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.errors.run_time import NotFoundException
from app.db.repositories.base import BaseRepository, ModelType
from app.db.tables.user_session import UserSession
from app.schemas.db.user_session import UserSessionDB


class UserSessionRepository(BaseRepository):
    async def get(self, session: Session, user_session_id: int) -> ModelType:
        stmt = select(self.model).where(self.model.id == user_session_id)
        return await session.scalar(stmt.order_by(self.model.id))

    async def get_by_user(self, session: Session, user_id: int) -> UserSessionDB:
        stmt = select(self.model).where(self.model.user_id == user_id)
        data = await session.scalar(stmt.order_by(self.model.id))
        if not data:
            raise NotFoundException
        return UserSessionDB.from_orm(data)

    async def create(
        self, session: Session, user_id: int, token: str, expires_at: datetime
    ) -> int | None:
        user_session_data = self.model(
            user_id=user_id,
            access_token=token,
            expires_at=expires_at,
        )
        session.add(user_session_data)
        try:
            await session.flush()
        except IntegrityError:
            return None
        return user_session_data.id

    async def delete_session(self, session: Session, user_id: int) -> bool:
        stmt = delete(self.model).where(self.model.user_id == user_id)
        result = await session.execute(stmt)
        await session.commit()
        return result


user_session = UserSessionRepository(UserSession)
