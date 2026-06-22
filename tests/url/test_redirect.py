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
    assert redirect_resp.headers["Location"] == "https://google.com/"


async def test_redirect_not_found(client: AsyncClient) -> None:
    redirect_resp = await client.get("/url/notexist", follow_redirects=False)

    assert redirect_resp.status_code == status.HTTP_404_NOT_FOUND


async def test_redirect_invalid_slug(client: AsyncClient) -> None:
    invalid_slug = "verylong" * 21  # max slug size = 20
    redirect_resp = await client.get(f"/url/{invalid_slug}", follow_redirects=False)

    assert redirect_resp.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
