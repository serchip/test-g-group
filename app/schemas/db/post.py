from datetime import datetime

from pydantic import BaseModel


class PostDB(BaseModel):
    id: int
    title: str
    description: str | None
    create_at: datetime

    class Config:
        orm_mode = True
