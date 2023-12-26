from pydantic import BaseModel


class UserDB(BaseModel):
    id: int
    email: str
    hashed_password: bytes
    is_active: bool
    first_name: str | None
    last_name: str | None
    # posts: list[Post]

    class Config:
        orm_mode = True
