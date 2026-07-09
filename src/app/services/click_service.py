from typing import Sequence

from src.app.core.enums import UserRole
from src.app.core.exceptions import PermissionDeniedError
from src.app.repositories.click import ClickRepository
from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.schemas.click import ClickResponse


class ClickService:
    def __init__(self, repo: ClickRepository, url_repo: ShortUrlRepository) -> None:
        self.repo = repo
        self.url_repo = url_repo

    async def get_stats(
        self, user_id: int, user_role: UserRole, url_id: int
    ) -> Sequence[ClickResponse]:
        url = await self.url_repo.get_url_by_id(url_id)

        if url.owner_id != user_id and user_role != "admin":
            raise PermissionDeniedError("You dont have permission to view it")

        stats = await self.repo.get_clicks_by_url_id(url.id)

        return [ClickResponse.model_validate(stat) for stat in stats]
