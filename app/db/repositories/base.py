from typing import Type, TypeVar

from app.db.tables.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository:
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model
