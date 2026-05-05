"""Integration tests for the /api/v1/auth endpoints."""

import pytest
from httpx import AsyncClient

BASE = "/api/v1/auth"

VALID_EMAIL = "alice@example.com"
VALID_PASSWORD = "supersecret1"


@pytest.mark.asyncio
class TestRegister:
    """POST /auth/register"""

    async def test_register_success(self, client: AsyncClient) -> None:
        resp = await client.post(
            f"{BASE}/register",
            json={
                "email": VALID_EMAIL,
                "password": VALID_PASSWORD,
                "full_name": "Alice",
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == VALID_EMAIL
        assert "hashed_password" not in body

    async def test_register_duplicate_email(self, client: AsyncClient) -> None:
        payload = {"email": "bob@example.com", "password": VALID_PASSWORD}
        await client.post(f"{BASE}/register", json=payload)
        resp = await client.post(f"{BASE}/register", json=payload)
        assert resp.status_code == 409

    async def test_register_invalid_email(self, client: AsyncClient) -> None:
        resp = await client.post(
            f"{BASE}/register",
            json={"email": "not-an-email", "password": VALID_PASSWORD},
        )
        assert resp.status_code == 422

    async def test_register_short_password(self, client: AsyncClient) -> None:
        resp = await client.post(
            f"{BASE}/register",
            json={"email": "charlie@example.com", "password": "short"},
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestLogin:
    """POST /auth/login"""

    async def test_login_success_sets_cookies(self, client: AsyncClient) -> None:
        await client.post(
            f"{BASE}/register",
            json={"email": "dave@example.com", "password": VALID_PASSWORD},
        )
        resp = await client.post(
            f"{BASE}/login",
            json={"email": "dave@example.com", "password": VALID_PASSWORD},
        )
        assert resp.status_code == 200
        set_cookie_headers = resp.headers.get_list("set-cookie")
        cookie_names = [h.split("=")[0].strip() for h in set_cookie_headers]
        assert "access_token" in cookie_names
        assert "refresh_token" in cookie_names

    async def test_login_wrong_password(self, client: AsyncClient) -> None:
        await client.post(
            f"{BASE}/register",
            json={"email": "eve@example.com", "password": VALID_PASSWORD},
        )
        resp = await client.post(
            f"{BASE}/login",
            json={"email": "eve@example.com", "password": "wrongpassword1"},
        )
        assert resp.status_code == 401

    async def test_login_unknown_email(self, client: AsyncClient) -> None:
        resp = await client.post(
            f"{BASE}/login",
            json={"email": "ghost@example.com", "password": VALID_PASSWORD},
        )
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestRefresh:
    """POST /auth/refresh"""

    async def test_refresh_issues_new_tokens(self, client: AsyncClient) -> None:
        await client.post(
            f"{BASE}/register",
            json={"email": "frank@example.com", "password": VALID_PASSWORD},
        )
        login_resp = await client.post(
            f"{BASE}/login",
            json={"email": "frank@example.com", "password": VALID_PASSWORD},
        )
        # Extract the refresh token from the Set-Cookie header to send it manually.
        set_cookies = login_resp.headers.get_list("set-cookie")
        refresh_token_value = next(
            (
                h.split("=", 1)[1].split(";")[0]
                for h in set_cookies
                if h.startswith("refresh_token")
            ),
            None,
        )
        assert refresh_token_value is not None, (
            "Login did not set a refresh_token cookie"
        )

        refresh_resp = await client.post(
            f"{BASE}/refresh",
            cookies={"refresh_token": refresh_token_value},
        )
        assert refresh_resp.status_code == 200
        new_set_cookies = refresh_resp.headers.get_list("set-cookie")
        new_access_value = next(
            (
                h.split("=", 1)[1].split(";")[0]
                for h in new_set_cookies
                if h.startswith("access_token")
            ),
            None,
        )
        assert new_access_value is not None
        # Verify the new token is a well-formed JWT (three dot-separated segments).
        assert new_access_value.count(".") == 2

    async def test_refresh_without_cookie_returns_401(
        self, client: AsyncClient
    ) -> None:
        # Client has no cookies yet
        fresh_client = AsyncClient(
            transport=client._transport,  # type: ignore[attr-defined]
            base_url="http://test",
        )
        async with fresh_client:
            resp = await fresh_client.post(f"{BASE}/refresh")
        assert resp.status_code == 401


@pytest.mark.asyncio
class TestLogout:
    """POST /auth/logout"""

    async def test_logout_clears_cookies(self, client: AsyncClient) -> None:
        await client.post(
            f"{BASE}/register",
            json={"email": "grace@example.com", "password": VALID_PASSWORD},
        )
        await client.post(
            f"{BASE}/login",
            json={"email": "grace@example.com", "password": VALID_PASSWORD},
        )
        resp = await client.post(f"{BASE}/logout")
        assert resp.status_code == 204
        # Cookies should be cleared (empty or absent)
        assert resp.cookies.get("access_token", "") == ""
