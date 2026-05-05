"""Tests for the health endpoint."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_ok(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "version" in body


@pytest.mark.asyncio
async def test_health_version_matches_settings(client: AsyncClient) -> None:
    from core.config import settings

    resp = await client.get("/api/v1/health")
    assert resp.json()["version"] == settings.APP_VERSION
