from slowapi import Limiter
from slowapi.util import get_remote_address

from src.app.core.settings import settings


limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis.rate_limiter_url,
    default_limits=["10/minute"],
)
