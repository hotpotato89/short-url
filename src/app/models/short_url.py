from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.models.base import Base


if TYPE_CHECKING:
    from src.app.models.user import User


class ShortUrl(Base):
    __tablename__ = "short_urls"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    original_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(20), nullable=False, unique=True, index=True
    )
    clicks: Mapped[int] = mapped_column(default=0)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, default=None
    )

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    owner: Mapped["User"] = relationship("User")
