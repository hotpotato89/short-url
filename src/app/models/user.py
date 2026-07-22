from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import TIMESTAMP, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.core.enums import UserRole
from src.app.models.base import Base


if TYPE_CHECKING:
    from src.app.models.export_log import ExportLog


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
    role: Mapped[UserRole] = mapped_column(
        String(20), default=UserRole.USER, nullable=False
    )

    is_superadmin: Mapped[bool] = mapped_column(nullable=True, default=False)

    credits: Mapped[int] = mapped_column(default=5)

    export_logs: Mapped[List["ExportLog"]] = relationship(
        "ExportLog", back_populates="user", lazy="selectin"
    )
