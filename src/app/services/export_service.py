import csv
import json
from io import BytesIO, StringIO
from typing import Sequence

import pandas as pd

from src.app.core.enums import ExportFormat
from src.app.core.exceptions import PermissionDeniedError
from src.app.models.short_url import ShortUrl
from src.app.repositories.export_log_repository import ExportLogRepository
from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.schemas.export_log import ExportLogResponse


class ExportService:
    def __init__(self, repo: ShortUrlRepository, log_repo: ExportLogRepository) -> None:
        self.repo = repo
        self.log_repo = log_repo

    async def get_logs(
        self, is_superadmin: bool, user_id: int | None = None, limit: int = 100
    ) -> Sequence[ExportLogResponse]:
        if is_superadmin is False:
            raise PermissionDeniedError("Only for supeadmin")

        if user_id:
            result = await self.log_repo.get_logs_by_user_id(limit, user_id)
        else:
            result = await self.log_repo.get_all_logs(limit)

        return [ExportLogResponse.model_validate(u) for u in result]

    async def export(self, format: ExportFormat = ExportFormat.CSV) -> str | bytes:
        urls = await self.repo.get_all()

        if format == ExportFormat.CSV:
            return self._csv_format(urls)
        elif format == ExportFormat.JSON:
            return self._json_format(urls)
        elif format == ExportFormat.XLSX:
            return self._xlsx_format(urls)

    def _json_format(self, urls: Sequence[ShortUrl]) -> str:
        data = [
            {
                "id": url.id,
                "original_url": url.original_url,
                "slug": url.slug,
                "clicks": url.clicks,
                "owner_id": url.owner_id,
                "created_at": url.created_at.isoformat(),
                "expires_at": url.expires_at.isoformat() if url.expires_at else None,
            }
            for url in urls
        ]
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _csv_format(self, urls: Sequence[ShortUrl]) -> str:
        output = StringIO()
        writer = csv.writer(output)

        writer.writerow(
            [
                "ID",
                "Original URL",
                "Slug",
                "Clicks",
                "Owner ID",
                "Created At",
                "Expires At",
            ]
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
                    url.expires_at.isoformat() if url.expires_at else None,
                ]
            )

        return output.getvalue()

    def _xlsx_format(self, urls: Sequence[ShortUrl]) -> bytes:
        data = [
            {
                "ID": url.id,
                "Original URL": url.original_url,
                "Slug": url.slug,
                "Clicks": url.clicks,
                "Owner ID": url.owner_id,
                "Created At": url.created_at.isoformat(),
                "Expires At": url.expires_at.isoformat() if url.expires_at else None,
            }
            for url in urls
        ]

        df = pd.DataFrame(data)
        output = BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="URLs", index=False)

        return output.getvalue()
