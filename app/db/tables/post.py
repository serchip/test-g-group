from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None]
    create_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    user_id: Mapped[int] = mapped_column(
        "user_id", ForeignKey("user.id"), nullable=False
    )
    user: Mapped[User] = relationship("User", back_populates="posts")
