from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class Token(BaseModel):
    # standard fields
    sub: int
    exp: datetime
    nbf: datetime
    iat: datetime
    aud: list[str]

    # custom fields
    email: str | None
    settings: dict[str, Any] = dict()

    @property
    def id(self) -> UUID:
        return self.sub
