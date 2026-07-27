"""
Sentinel AI — Phase 6A Plugin Engine & Extension SDK Test Suite

Tests PluginManifest schema validation, PluginLoader, PluginLifecycle, PluginRegistry,
PluginEngine, PluginService, and REST API endpoints.
"""

import pytest
from pydantic import ValidationError

from app.models.enums import PluginStatus, PluginType
from app.plugins.engine import PluginEngine
from app.plugins.loader import PluginLoader
from app.plugins.manifest import PluginManifest
from app.services.plugin_service import PluginService


# ── Manifest Validation Tests ──────────────────────────────────────────────────
def test_plugin_manifest_validation():
    """Test plugin.yaml manifest parsing and schema validation rules."""
    # Valid Manifest
    mdict = {
        "id": "sentinel.plugin.test.custom",
        "name": "Custom Test Plugin",
        "version": "1.0.0",
        "author": "Tester",
        "description": "Test plugin description",
        "plugin_type": "connector",
        "entry_point": "test.main:CustomPlugin",
        "minimum_platform_version": "1.0.0",
        "permissions": ["data:read"],
    }
    manifest = PluginManifest(**mdict)
    assert manifest.id == "sentinel.plugin.test.custom"
    assert manifest.plugin_type == PluginType.CONNECTOR

    # Invalid Manifest (ID missing dots)
    with pytest.raises(ValidationError):
        PluginManifest(
            id="invalidid",
            name="Invalid",
            version="1.0.0",
            author="Tester",
            description="Test",
            plugin_type="connector",
            entry_point="test.main",
        )


# ── Plugin Loader & Engine Tests ──────────────────────────────────────────────
def test_plugin_loader_and_engine():
    """Test PluginLoader manifest instantiation and PluginEngine lifecycle state transitions."""
    loader = PluginLoader()
    engine = PluginEngine()

    p = loader.load_from_manifest_data({
        "id": "sentinel.plugin.loader.test",
        "name": "Loader Test Plugin",
        "version": "1.0.0",
        "author": "Tester",
        "description": "Test",
        "plugin_type": "validation_rule",
        "entry_point": "test.main",
    })
    assert p.status == PluginStatus.VALIDATED

    # Register & Enable
    engine._registry.register(p)
    enabled_p = engine.enable_plugin(p.plugin_id)
    assert enabled_p.status == PluginStatus.ENABLED

    # Execute
    res = engine.execute_plugin(p.plugin_id, {"key": "val"})
    assert res["status"] == "success"

    # Disable
    disabled_p = engine.disable_plugin(p.plugin_id)
    assert disabled_p.status == PluginStatus.DISABLED

    # Execute on disabled should raise ValueError
    with pytest.raises(ValueError):
        engine.execute_plugin(p.plugin_id)


@pytest.mark.asyncio
async def test_plugin_service_and_rest_api(client, auth_headers, db_session):
    """Test PluginService and REST API endpoints /plugins, /{id}, /{id}/enable, /{id}/disable, /reload."""
    svc = PluginService(db_session)
    plugins = await svc.discover_plugins()
    await db_session.commit()
    assert len(plugins) >= 3

    target_id = "sentinel.plugin.connector.snowflake"

    # 1. Get List via GET
    resp_list = await client.get("/api/v1/plugins", headers=auth_headers)
    assert resp_list.status_code == 200
    assert len(resp_list.json()) >= 3

    # 2. Get Detail via GET
    resp_detail = await client.get(f"/api/v1/plugins/{target_id}", headers=auth_headers)
    assert resp_detail.status_code == 200
    assert resp_detail.json()["plugin_id"] == target_id

    # 3. Enable via POST
    resp_enable = await client.post(f"/api/v1/plugins/{target_id}/enable", headers=auth_headers)
    assert resp_enable.status_code == 200
    assert resp_enable.json()["status"] == "enabled"

    # 4. Disable via POST
    resp_disable = await client.post(f"/api/v1/plugins/{target_id}/disable", headers=auth_headers)
    assert resp_disable.status_code == 200
    assert resp_disable.json()["status"] == "disabled"

    # 5. Reload via POST
    resp_reload = await client.post("/api/v1/plugins/reload", headers=auth_headers)
    assert resp_reload.status_code == 200
