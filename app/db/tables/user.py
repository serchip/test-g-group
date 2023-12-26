from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[bytes]
    is_active: Mapped[bool] = mapped_column(default=True)
    first_name: Mapped[str | None] = mapped_column(String(30))
    last_name: Mapped[str | None] = mapped_column(String(30))
    session: Mapped[UserSession] = relationship(
        "UserSession",
        uselist=False,
        backref="user",
        cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )
    posts: Mapped[list[Post]] = relationship(
        "Post",
        back_populates="user",
        order_by="Post.id",
        cascade="save-update, merge, refresh-expire, expunge, delete, delete-orphan",
    )


from .post import Post
from .user_session import UserSession
