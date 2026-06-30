from sqlalchemy.orm import Session

from src.app.core.exceptions import SlugNotFoundError
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