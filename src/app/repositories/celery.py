from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.app.core.exceptions import SlugNotFoundError
from src.app.models.export_log import ExportLog
from src.app.models.short_url import ShortUrl


class CeleryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def increment_clicks(self, slug: str) -> None:
        result = self.session.query(ShortUrl).filter(ShortUrl.slug == slug)
        url = result.scalar()
        if not url:
            raise SlugNotFoundError(f"URL with slug '{slug}' not found")
        url.clicks += 1
        self.session.commit()

    def delete_expired(self) -> int:
        stmt = delete(ShortUrl).where(ShortUrl.expires_at < datetime.now(timezone.utc))
        result = self.session.execute(stmt)
        self.session.commit()
        if hasattr(result, "rowcount"):
            return result.rowcount  # type: ignore
        else:
            return 0

    def save_export_logs(
        self, user_id: int, format: Literal["csv", "json", "xlsx"]
    ) -> None:
        new_log = ExportLog(user_id=user_id, format=format)
        self.session.add(new_log)
        self.session.commit()
