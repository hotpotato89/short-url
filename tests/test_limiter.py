import pytest
from fastapi import status
from httpx import AsyncClient

from src.app.schemas.token import TokenInfo
from src.app.core.limiter import limiter


async def test_limiter(client: AsyncClient, auth_tokens: TokenInfo) -> None:
    """
    
    This test has realy cooldown, please wait 1 minute before run tests again :)

    """
    old_storage_uri = limiter._storage_uri
    old_storage = limiter._storage
    
    limiter._storage_uri = None
    limiter._storage = None #type: ignore
    limiter.enabled = True

    results: list[int] = []

    for _ in range(11):
        resp = await client.post(
            "/url",
            json={"original_url": "https://example.com"},
            headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
        )
        results.append(resp.status_code)

    assert results == [status.HTTP_200_OK] * 10 + [status.HTTP_429_TOO_MANY_REQUESTS]


    limiter._storage_uri = old_storage_uri
    limiter._storage = old_storage

    limiter.enabled = False
