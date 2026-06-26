from datetime import datetime
from typing import TYPE_CHECKING, Literal

from sqlalchemy import TIMESTAMP, func, String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.models.base import Base


if TYPE_CHECKING:
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    role: Mapped[Literal["user", "admin"]] = mapped_column(
        String(20), default="user", nullable=False
    )
