from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String

from src.app.models.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token: Mapped[str] = mapped_column(String(500), nullable=False, index=True, primary_key=True)
