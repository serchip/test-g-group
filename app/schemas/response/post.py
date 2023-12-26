from datetime import datetime

from pydantic import BaseModel


class PostsList(BaseModel):
    id: int
    title: str | None
    description: str | None
    create_at: datetime


class PostsListResponse(BaseModel):
    posts: list[PostsList]
    total: int


class PostGetResponse(BaseModel):
    id: int
    title: str | None
    description: str | None
    create_at: datetime
