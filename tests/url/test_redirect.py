from httpx import AsyncClient
import pytest
from fastapi import status

from src.app.schemas.short_url import UrlResponse


async def test_redirect(client: AsyncClient, auth_token: str) -> None:
    url_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    assert url_resp.status_code == status.HTTP_200_OK

    url_data = UrlResponse(**url_resp.json())

    redirect_resp = await client.get(f"/url/{url_data.slug}", follow_redirects=False)

    assert redirect_resp.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert redirect_resp.headers['Location'] == 'https://google.com/'
