from httpx import AsyncClient
import pytest
from fastapi import status

from src.app.schemas.token import TokenInfo


async def test_refresh(client: AsyncClient, auth_tokens: TokenInfo) -> None:
    refresh_resp = await client.post(
        "/auth/refresh", json={"refresh_token": auth_tokens.refresh_token}
    )

    refresh_data = TokenInfo(**refresh_resp.json())

    assert hasattr(refresh_data, "access_token")
    assert hasattr(refresh_data, "refresh_token")
    assert hasattr(refresh_data, "type")


async def test_refresh_invalid(client: AsyncClient) -> None:
    refresh_resp = await client.post(
        "/auth/refresh", json={"refresh_token": "not-a-token"}
    )

    assert refresh_resp.status_code == status.HTTP_401_UNAUTHORIZED


async def test_refresh_invalid_type(
    client: AsyncClient, auth_tokens: TokenInfo
) -> None:
    refresh_resp = await client.post(
        "/auth/refresh", json={"refresh_token": auth_tokens.access_token}
    )

    assert refresh_resp.status_code == status.HTTP_401_UNAUTHORIZED


async def test_refresh_reuse(client: AsyncClient, auth_tokens: TokenInfo) -> None:
    """

    This test broke, and I don't know why.
    I was supposed to delete the old token and create a new one, which would invalidate the old token.
    But for some reason, it remains valid.
    I spent three hours debugging it, and it was unsuccessful.
    ---------------------------------------------------------------------------
    In manual testing, everything works perfectly.

    """
    refresh_resp1 = await client.post(
        "/auth/refresh", json={"refresh_token": auth_tokens.refresh_token}
    )
    assert refresh_resp1.status_code == status.HTTP_200_OK

    refresh_resp2 = await client.post(
        "/auth/refresh", json={"refresh_token": auth_tokens.refresh_token}
    )
    assert refresh_resp2.status_code == status.HTTP_401_UNAUTHORIZED
