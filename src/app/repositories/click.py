from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.exceptions import ClickNotFoundError
from src.app.models.click import Click


class ClickRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_click_by_id(self, click_id: int) -> Click:
        stmt = select(Click).where(Click.id == click_id)
        result = await self.session.execute(stmt)
        click = result.scalar_one_or_none()
        if not click:
            raise ClickNotFoundError(f"Click with id {click_id} not found")
        return click

    async def get_clicks_by_url_id(
        self, url_id: int, limit: int = 10, cursor: int | None = None
    ) -> Sequence[Click]:
        stmt = (
            select(Click)
            .where(Click.url_id == url_id)
            .order_by(Click.id.desc())
            .limit(limit + 1)
        )
        if cursor is not None:
            stmt = stmt.where(Click.id < cursor)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def save_click(self, url_id: int, user_ip: str, user_agent: str) -> None:
        new_click = Click(url_id=url_id, user_ip=user_ip, user_agent=user_agent)
        self.session.add(new_click)
        await self.session.flush()
