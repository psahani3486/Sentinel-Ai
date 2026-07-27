"""
Sentinel AI — Health Endpoint Tests
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    """GET /api/v1/health should return 200 with app info."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_check_has_correct_content_type(client: AsyncClient) -> None:
    """Health endpoint should return JSON content type."""
    response = await client.get("/api/v1/health")
    assert "application/json" in response.headers["content-type"]
