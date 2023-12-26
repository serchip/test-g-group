from pydantic import BaseModel


class UserSessionDB(BaseModel):
    id: int
    access_token: str
    user_id: int

    class Config:
        orm_mode = True
