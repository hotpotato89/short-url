import pytest
from httpx import AsyncClient
from fastapi import status

from src.app.schemas.token import TokenInfo


async def test_qrcode_response_is_png(
    client: AsyncClient, auth_tokens: TokenInfo
) -> None:
    url_resp = await client.post(
        "/url",
        json={"original_url": "https://google.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )

    slug = url_resp.json()["slug"]

    assert url_resp.status_code == status.HTTP_200_OK

    qrcode_resp = await client.get(f"/url/{slug}/qr")

    assert qrcode_resp.status_code == status.HTTP_200_OK
    assert qrcode_resp.headers["content-type"] == "image/png"
    content = qrcode_resp.content
    assert len(content) > 100
    assert content[:8] == b"\x89PNG\r\n\x1a\n"


async def test_qrcode_not_found(client: AsyncClient) -> None:
    resp = await client.get("/url/nonexist/qr")

    assert resp.status_code == status.HTTP_404_NOT_FOUND


async def test_qrcode_invalidation(client: AsyncClient, auth_tokens: TokenInfo) -> None:
    create_rep = await client.post(
        "/url",
        json={"original_url": "https://example.com"},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    slug = create_rep.json()["slug"]

    assert create_rep.status_code == status.HTTP_200_OK

    qr1 = await client.get(f"/url/{slug}/qr")
    assert qr1.status_code == status.HTTP_200_OK

    new_slug = "new-slug"
    edit_resp = await client.put(
        f"/url/{slug}",
        json={"slug": new_slug},
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert edit_resp.status_code == status.HTTP_200_OK

    qr_old = await client.get(f"/url/{slug}/qr")
    assert qr_old.status_code == status.HTTP_404_NOT_FOUND

    qr_new = await client.get(f"/url/{new_slug}/qr")
    assert qr_new.status_code == status.HTTP_200_OK
