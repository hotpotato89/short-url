import pandas as pd
import io
import pytest
from fastapi import status
from httpx import AsyncClient

from src.app.schemas.token import TokenInfo


async def test_admin_export_denied_for_user(
    client: AsyncClient,
    auth_tokens: TokenInfo,
) -> None:
    resp = await client.get(
        "/url/admin/export",
        headers={"Authorization": f"Bearer {auth_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN


async def test_admin_export_allowed_for_admin(
    client: AsyncClient,
    admin_tokens: TokenInfo,
) -> None:
    resp = await client.get(
        "/url/admin/export?format=json",
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers["content-type"] == "application/json"


async def test_admin_export_csv(
    client: AsyncClient,
    admin_tokens: TokenInfo,
) -> None:
    resp = await client.get(
        "/url/admin/export?format=csv",
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )

    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in resp.headers["content-disposition"]
    assert resp.headers["content-disposition"].endswith('.csv"')

    content = resp.text
    assert "ID" in content
    assert "Slug" in content
    assert "Original URL" in content


async def test_admin_export_json(
    client: AsyncClient,
    admin_tokens: TokenInfo,
) -> None:
    resp = await client.get(
        "/url/admin/export?format=json",
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )

    assert resp.status_code == status.HTTP_200_OK
    assert resp.headers["content-type"] == "application/json"
    assert "attachment" in resp.headers["content-disposition"]
    assert resp.headers["content-disposition"].endswith('.json"')

    data = resp.json()
    assert isinstance(data, list)

    if len(data) > 0:
        first = data[0]
        assert "id" in first
        assert "slug" in first
        assert "original_url" in first
        assert "clicks" in first


async def test_jwt_contains_role(
    client: AsyncClient,
    admin_user,
) -> None:
    login_resp = await client.post(
        "/auth/login",
        json={
            "email": admin_user.email,
            "password": "admin123",
        },
    )
    assert login_resp.status_code == status.HTTP_200_OK

    data = login_resp.json()
    from src.app.utils.jwt import decode_jwt

    payload = decode_jwt(data["access_token"])
    assert payload["role"] == "admin"


async def test_admin_export_empty(
    client: AsyncClient,
    admin_tokens: TokenInfo,
) -> None:
    resp = await client.get(
        "/url/admin/export?format=json",
        headers={"Authorization": f"Bearer {admin_tokens.access_token}"},
    )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert isinstance(data, list)


async def test_export_xlsx(
    client: AsyncClient,
    admin_tokens: TokenInfo,
) -> None:
    headers = {"Authorization": f"Bearer {admin_tokens.access_token}"}

    create_resp = await client.post(
        "/url",
        json={"original_url": "https://example.com/xlsx-test"},
        headers=headers,
    )
    assert create_resp.status_code == 200

    response = await client.get("/url/admin/export?format=xlsx", headers=headers)
    assert response.status_code == 200
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "attachment" in response.headers["content-disposition"]

    df = pd.read_excel(io.BytesIO(response.content))

    expected_columns = [
        "ID",
        "Original URL",
        "Slug",
        "Clicks",
        "Owner ID",
        "Created At",
        "Expires At",
    ]

    for col in expected_columns:
        assert col in df.columns

    assert len(df) > 0
    assert df.iloc[0]["Original URL"] == "https://example.com/xlsx-test"
