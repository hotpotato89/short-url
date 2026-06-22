import pytest
from httpx import AsyncClient
from fastapi import status

from src.app.schemas.token import TokenInfo


async def test_logout(client: AsyncClient, auth_tokens: TokenInfo) -> None:
    logout_resp = await client.post(
        "/auth/logout", json={"refresh_token": auth_tokens.refresh_token}
    )

    assert logout_resp.status_code == status.HTTP_204_NO_CONTENT


async def test_logout_delete_token(client: AsyncClient, auth_tokens: TokenInfo) -> None:
    logout_resp = await client.post(
        "/auth/logout", json={"refresh_token": auth_tokens.refresh_token}
    )

    assert logout_resp.status_code == status.HTTP_204_NO_CONTENT

    refresh_resp = await client.post(
        "/auth/refresh", json={"refresh_token": auth_tokens.refresh_token}
    )

    assert refresh_resp.status_code == status.HTTP_401_UNAUTHORIZED
