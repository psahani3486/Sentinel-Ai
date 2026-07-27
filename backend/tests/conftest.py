"""
Sentinel AI — Test Configuration & Fixtures

Provides:
- Async test client using httpx
- In-memory test database session override
- Pre-registered test user fixture
"""

import asyncio
import os
import uuid
from collections.abc import AsyncGenerator
from typing import Any

# Ensure testing environment for pytest
os.environ["ENVIRONMENT"] = "testing"
from app.config.settings import get_settings
get_settings.cache_clear()

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import hash_password
from app.db.session import get_async_session
from app.core.limiter import limiter
from app.main import app
from app.models.base import Base
from app.models.user import User, UserRole

# Disable rate limiting for the test suite
limiter.enabled = False

# Use SQLite for tests (async via aiosqlite) to avoid PostgreSQL dependency in CI
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    """Override the DB session dependency with the test database."""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Override the database dependency
app.dependency_overrides[get_async_session] = override_get_session


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session fixture for direct unit tests."""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user_data() -> dict[str, Any]:
    """Raw data for creating a test user."""
    return {
        "email": f"test-{uuid.uuid4().hex[:8]}@sentinel-ai.io",
        "password": "TestPassword123!",
        "full_name": "Test User",
    }


@pytest_asyncio.fixture
async def registered_user(
    client: AsyncClient, test_user_data: dict[str, Any]
) -> dict[str, Any]:
    """Register a user and return their data + response."""
    response = await client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    return {**test_user_data, "user": response.json()}


@pytest_asyncio.fixture
async def auth_headers(
    client: AsyncClient, registered_user: dict[str, Any]
) -> dict[str, str]:
    """Get authentication headers for a registered user."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create and return a standard test User ORM entity."""
    user = User(
        email=f"test-{uuid.uuid4().hex[:8]}@sentinel-ai.io",
        hashed_password=hash_password("Password123!"),
        full_name="Standard Test User",
        role=UserRole.DATA_ENGINEER,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user() -> dict[str, Any]:
    """Create an admin user directly in the test database."""
    async with TestSessionLocal() as session:
        admin = User(
            email=f"admin-{uuid.uuid4().hex[:8]}@sentinel-ai.io",
            hashed_password=hash_password("AdminPassword123!"),
            full_name="Test Admin",
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        return {
            "id": str(admin.id),
            "email": admin.email,
            "password": "AdminPassword123!",
        }


@pytest_asyncio.fixture
async def admin_headers(
    client: AsyncClient, admin_user: dict[str, Any]
) -> dict[str, str]:
    """Get authentication headers for an admin user."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_user["email"],
            "password": admin_user["password"],
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
