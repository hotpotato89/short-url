from src.app.core.settings import settings
from src.app.repositories.short_url_repository import ShortUrlRepository
from src.app.utils.cache import cache, invalidate_cache
from src.app.utils.qrcode import generate_qr_base64


class QrcodeService:
    def __init__(self, repo: ShortUrlRepository) -> None:
        self.repo = repo

    @cache(3600 * 24, prefix='qr')
    async def get_qrcode(self, slug: str) -> str:
        url = await self.repo.get_url(slug)
        full_url = f'{settings.app.base_url}/url/{url}'
        return generate_qr_base64(full_url)
    
    async def invalidate_qrcode_cache(self, slug: str) -> None:
        await invalidate_cache(f'qr:{slug}')