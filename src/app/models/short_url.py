from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.app.models.base import Base
from src.app.models.mixins import IdPkMixin, TimestampMixin


class ShortUrl(TimestampMixin, IdPkMixin, Base):
    __tablename__ = "short_urls"

    original_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(20), nullable=False, unique=True, index=True
    )
    clicks: Mapped[int] = mapped_column(default=0)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, default=None
    )

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at
