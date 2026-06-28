from httpx import AsyncClient
import pytest
from src.app.schemas.token import TokenInfo
from uuid import uuid4
from fastapi import status
from time import perf_counter


async def test_cache_redirect(client: AsyncClient, auth_tokens: TokenInfo) -> None:
    resp = await client.post(
        "/url",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    slug = resp.json()["slug"]

    start = perf_counter()
    resp1 = await client.get(f"/url/{slug}")
    duration1 = perf_counter() - start
    assert resp1.status_code == status.HTTP_303_SEE_OTHER

    start = perf_counter()
    resp2 = await client.get(f"/url/{slug}")
    duration2 = perf_counter() - start
    assert resp2.status_code == status.HTTP_303_SEE_OTHER

    assert duration2 < duration1
