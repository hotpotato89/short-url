import csv
from io import StringIO
import json
from typing import Literal, Sequence

from src.app.models.short_url import ShortUrl
from src.app.repositories.short_url_repository import ShortUrlRepository


class ExportService:
    def __init__(self, repo: ShortUrlRepository) -> None:
        self.repo = repo

    async def export(self, format: Literal["csv", "json"] = "json") -> str:
        urls = await self.repo.get_all()

        if format == "csv":
            return self._csv_format(urls)
        elif format == "json":
            return self._json_format(urls)

    def _json_format(self, urls: Sequence) -> str:
        data = []
        for url in urls:
            data.append(
                {
                    "id": url.id,
                    "original_url": url.original_url,
                    "slug": url.slug,
                    "clicks": url.clicks,
                    "owner_id": url.owner_id,
                    "created_at": url.created_at.isoformat(),
                }
            )
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _csv_format(self, urls: Sequence[ShortUrl]) -> str:
        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(
            ["ID", "Original url", "Slug", "Clicks", "Owner ID", "Created at"]
        )

        for url in urls:
            writer.writerow(
                [
                    url.id,
                    url.original_url,
                    url.slug,
                    url.clicks,
                    url.owner_id,
                    url.created_at.isoformat(),
                ]
            )

        return output.getvalue()
