from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.app.models.base import Base
from src.app.models.mixins import IdPkMixin


class Click(IdPkMixin, Base):
    __tablename__ = "clicks"
    __table_args__ = (Index("ix_clicks_url_created", "url_id", "created_at"),)

    url_id: Mapped[int] = mapped_column(
        ForeignKey("short_urls.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    user_agent: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(True), server_default=func.now()
    )
