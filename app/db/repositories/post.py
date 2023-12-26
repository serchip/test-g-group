from typing import List

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.repositories.base import BaseRepository, ModelType
from app.db.tables.post import Post


class PostRepository(BaseRepository):
    async def get(self, session: Session, post_id: int, user_id: int) -> ModelType:
        stmt = select(self.model).where(
            self.model.id == post_id, self.model.user_id == user_id
        )
        return await session.scalar(stmt.order_by(self.model.id))

    async def list(
        self, session: Session, user_id: int, limit: int, offset: int
    ) -> List[ModelType]:
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        stream = await session.stream_scalars(stmt.order_by(self.model.id))
        async for row in stream:
            yield row

    async def count(
        self,
        session: Session,
        user_id: int,
    ) -> ModelType:
        stmt = select(func.count(self.model.id)).where(self.model.user_id == user_id)
        return await session.scalar(stmt)

    async def create(
        self,
        session: Session,
        title: str,
        user_id: int,
        description: str | None = None,
    ) -> int | None:
        row_data = self.model(
            title=title,
            description=description,
            user_id=user_id,
        )
        session.add(row_data)
        try:
            await session.commit()
        except IntegrityError:
            return None
        return row_data.id

    async def delete(self, session: Session, post_id: int, user_id: int) -> bool:
        stmt = delete(self.model).where(
            self.model.user_id == user_id, self.model.id == post_id
        )
        result = await session.execute(stmt)
        await session.commit()
        return result

    async def update(
        self,
        session: Session,
        title: str,
        post_id: int,
        user_id: int,
        description: str | None = None,
    ) -> int | None:
        stmt = (
            update(self.model)
            .where(self.model.user_id == user_id, self.model.id == post_id)
            .values(title=title, description=description)
        )
        await session.execute(stmt)
        await session.commit()
        return post_id


post = PostRepository(Post)
