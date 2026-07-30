from datetime import datetime

from sqlalchemy import TIMESTAMP, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.app.core.enums import UserRole
from src.app.models.base import Base
from src.app.models.mixins import IdPkMixin


class User(IdPkMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    role: Mapped[UserRole] = mapped_column(
        String(20), default=UserRole.USER, nullable=False
    )

    is_superadmin: Mapped[bool] = mapped_column(nullable=True, default=False)

    credits: Mapped[int] = mapped_column(default=5)
