from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.enums import ExportFormat
from src.app.models.export_log import ExportLog


class ExportLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_logs(
        self, limit: int = 100, cursor: int | None = None
    ) -> Sequence[ExportLog]:
        stmt = select(ExportLog).order_by(ExportLog.id.desc()).limit(limit)

        if cursor:
            stmt = stmt.where(ExportLog.id < cursor)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def save_export_logs(self, user_id: int, format: ExportFormat) -> None:
        new_log = ExportLog(user_id=user_id, format=format)
        self.session.add(new_log)
        await self.session.flush()
