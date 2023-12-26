from pydantic import BaseModel, EmailStr


class LoginInRequest(BaseModel):
    email: EmailStr
    password: str
