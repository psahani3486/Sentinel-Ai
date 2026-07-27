"""
Sentinel AI — Authentication Endpoint Tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, test_user_data: dict) -> None:
    """POST /auth/register should create a new user with VIEWER role."""
    response = await client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["full_name"] == test_user_data["full_name"]
    assert data["role"] == "viewer"
    assert data["is_active"] is True
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(
    client: AsyncClient, registered_user: dict
) -> None:
    """Registering with an existing email should return 409."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": registered_user["email"],
            "password": "AnotherPassword123!",
            "full_name": "Another User",
        },
    )
    assert response.status_code == 409
    assert "already exists" in response.json()["message"]


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient) -> None:
    """Registering with an invalid email should return 422."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "Password123!",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient) -> None:
    """Registering with a short password should return 422."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "valid@example.com",
            "password": "short",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(
    client: AsyncClient, registered_user: dict
) -> None:
    """POST /auth/login with valid credentials should return tokens."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(
    client: AsyncClient, registered_user: dict
) -> None:
    """POST /auth/login with wrong password should return 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["email"],
            "password": "WrongPassword123!",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    """POST /auth/login with unknown email should return 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "ghost@sentinel-ai.io",
            "password": "Password123!",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(
    client: AsyncClient, auth_headers: dict, registered_user: dict
) -> None:
    """GET /auth/me should return the authenticated user's profile."""
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["email"] == registered_user["email"]
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_get_current_user_no_token(client: AsyncClient) -> None:
    """GET /auth/me without a token should return 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(
    client: AsyncClient, registered_user: dict
) -> None:
    """POST /auth/refresh should return new tokens."""
    # First login to get tokens
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_users_endpoint_requires_admin(
    client: AsyncClient, auth_headers: dict
) -> None:
    """GET /users should return 403 for non-admin users."""
    response = await client.get("/api/v1/users", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_list_users(
    client: AsyncClient, admin_headers: dict
) -> None:
    """GET /users should return paginated list for admin users."""
    response = await client.get("/api/v1/users", headers=admin_headers)
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
