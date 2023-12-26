from __future__ import annotations

import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    access_token: Mapped[str] = mapped_column(String(255))
    create_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    expires_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    user_id: Mapped[int] = mapped_column(
        "user_id", ForeignKey("user.id"), nullable=False
    )
