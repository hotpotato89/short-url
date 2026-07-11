from src.app.core.settings import settings
from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.utils.qrcode import generate_qr_base64
from src.app.core.redis_client import cache_manager


class QrcodeService:
    def __init__(self, repo: ShortUrlRepository) -> None:
        self.repo = repo

    @cache_manager.cache(3600 * 24, prefix="qr")
    async def get_qrcode(self, slug: str) -> str:
        url = await self.repo.get_url(slug)
        full_url = f"{settings.app.base_url}/url/{url.slug}"
        return generate_qr_base64(full_url)

    async def invalidate_qrcode_cache(self) -> None:
        await cache_manager.invalidate_cache("qr")
