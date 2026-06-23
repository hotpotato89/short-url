from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user_id: int, refresh_token: str) -> RefreshToken:
        new_token = RefreshToken(user_id=user_id, token=refresh_token)
        self.session.add(new_token)
        await self.session.flush()
        return new_token

    async def get_by_token(self, refresh_token: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token)
        )
        token = result.scalar_one_or_none()
        if not token:
            return
        return token

    async def delete_by_token(self, refresh_token: str) -> None:
        token = await self.session.get(RefreshToken, refresh_token)
        if token:
            await self.session.delete(token)
            await self.session.flush()
