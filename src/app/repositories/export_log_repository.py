from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.export_log import ExportLog


class ExportLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_logs(self, limit: int = 100) -> Sequence[ExportLog]:
        result = await self.session.execute(
            select(ExportLog).order_by(ExportLog.created_at.desc()).limit(limit)
        )
        return result.scalars().all()

    async def get_logs_by_user_id(
        self, limit: int, user_id: int
    ) -> Sequence[ExportLog]:
        result = await self.session.execute(
            select(ExportLog)
            .where(ExportLog.user_id == user_id)
            .order_by(ExportLog.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
