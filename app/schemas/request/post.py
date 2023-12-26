from pydantic import BaseModel


class CreatePostInRequest(BaseModel):
    title: str | None
    description: str | None
