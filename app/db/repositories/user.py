from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository, ModelType
from app.db.tables.user import User
from app.schemas.db.user import UserDB


class UserRepository(BaseRepository):
    async def get(self, session: Session, user_id: int) -> ModelType:
        stmt = select(self.model).where(self.model.id == user_id)
        return await session.scalar(stmt.order_by(self.model.id))

    async def get_by_email(self, session: Session, email: str) -> UserDB:
        stmt = select(self.model).where(self.model.email == email)
        data = await session.scalar(stmt.order_by(self.model.id))
        return UserDB.from_orm(data)

    async def list(self, session: Session) -> List[ModelType]:
        stmt = select(self.model)
        stream = await session.stream_scalars(stmt.order_by(self.model.id))
        async for row in stream:
            yield row

    async def create(
        self,
        session: Session,
        email: str,
        hashed_password: bytes,
        first_name: str = None,
        last_name: str = None,
    ) -> int | None:
        user_data = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            hashed_password=hashed_password,
        )
        session.add(user_data)
        try:
            await session.flush()
        except IntegrityError:
            return None
        return user_data.id


user = UserRepository(User)
