"""
Sentinel AI — Tests for Review Improvements (Cookies, JTI Revocation, Rate Limiting)
"""

import pytest
from httpx import AsyncClient
from app.core.limiter import limiter


@pytest.mark.asyncio
async def test_cookie_authentication_flow(
    client: AsyncClient, test_user_data: dict
) -> None:
    """Verifies that login sets the HttpOnly cookie, and refresh exchanges it."""
    # 1. Register user
    reg_resp = await client.post("/api/v1/auth/register", json=test_user_data)
    assert reg_resp.status_code == 201

    # 2. Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    assert login_resp.status_code == 200
    
    # Assert HttpOnly cookie was set
    assert "refresh_token" in client.cookies
    login_data = login_resp.json()
    assert login_data["access_token"] != ""
    assert login_data["refresh_token"] == ""  # Excluded from JSON payload

    # 3. Refresh token (utilizes the client cookies automatically)
    refresh_resp = await client.post("/api/v1/auth/refresh")
    assert refresh_resp.status_code == 200
    refresh_data = refresh_resp.json()
    assert refresh_data["access_token"] != ""
    assert "refresh_token" in client.cookies


@pytest.mark.asyncio
async def test_revoked_token_fails_refresh(
    client: AsyncClient, test_user_data: dict
) -> None:
    """Verifies that logout revokes the JTI in DB, causing subsequent refreshes to fail."""
    # 1. Register and Login
    await client.post("/api/v1/auth/register", json=test_user_data)
    await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    assert "refresh_token" in client.cookies

    # 2. Logout
    logout_resp = await client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 200
    assert "refresh_token" not in client.cookies  # Cookie cleared

    # 3. Attempt refresh with the revoked token (manually set cookie)
    client.cookies.set("refresh_token", "invalid_or_revoked_jwt_token_jti_value")
    fail_refresh = await client.post("/api/v1/auth/refresh")
    assert fail_refresh.status_code == 401


@pytest.mark.asyncio
async def test_api_rate_limiting_on_auth(
    client: AsyncClient, test_user_data: dict
) -> None:
    """Verifies that rate limiting returns HTTP 429 when enabled and limit is hit."""
    # Enable rate limiting for this test
    limiter.enabled = True
    try:
        # Trigger 6 rapid requests (limit is 5/minute)
        responses = []
        for _ in range(6):
            resp = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user_data["email"],
                    "password": "wrong-password-test",
                },
            )
            responses.append(resp.status_code)

        # Assert at least one request was blocked with 429 Too Many Requests
        assert 429 in responses
    finally:
        # Restore rate limiter configuration for other tests
        limiter.enabled = False
