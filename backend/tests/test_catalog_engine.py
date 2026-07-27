"""
Sentinel AI — Phase 6B Data Catalog, Lineage & Governance Test Suite

Tests Catalog Processors, Lineage DAG Graph Executor, CatalogEngine,
CatalogService, and REST API endpoints.
"""

import uuid
import pytest

from app.catalog.engine import CatalogEngine
from app.catalog.executor import CatalogExecutor
from app.catalog.processors import (
    DatasetCatalogProcessor,
    GovernancePolicyProcessor,
    WorkflowCatalogProcessor,
)
from app.services.catalog_service import CatalogService


# ── Processor & Lineage Tests ──────────────────────────────────────────────────
def test_catalog_processors_and_lineage_executor():
    """Test metadata extraction processors and lineage DAG graph construction."""
    d_proc = DatasetCatalogProcessor()
    meta1 = d_proc.process_asset({"name": "Test Dataset", "domain": "Finance"})
    assert meta1.name == "Test Dataset"

    w_proc = WorkflowCatalogProcessor()
    meta2 = w_proc.process_asset({"name": "Test Workflow"})
    assert meta2.name == "Test Workflow"

    g_proc = GovernancePolicyProcessor()
    meta3 = g_proc.process_asset({"name": "Test Policy"})
    assert meta3.name == "Test Policy"

    executor = CatalogExecutor()
    src_id = uuid.uuid4()
    tgt_id = uuid.uuid4()
    dag = executor.build_lineage_dag(src_id, tgt_id, "TRANSFORMS")
    assert dag["source"] == str(src_id)
    assert dag["target"] == str(tgt_id)


def test_catalog_engine():
    """Test CatalogEngine indexing."""
    engine = CatalogEngine()
    results = engine.index_assets({"name": "Engine Asset"})
    assert len(results) >= 3


@pytest.mark.asyncio
async def test_catalog_service_and_rest_api(client, auth_headers, db_session):
    """Test CatalogService and REST API endpoints /catalog/assets, /assets/{id}, /lineage/{id}, /glossary, and /policies."""
    svc = CatalogService(db_session)
    assets = await svc.seed_initial_catalog()
    await db_session.commit()
    assert len(assets) >= 2

    asset_id = str(assets[0].id)

    # 1. Get Assets via GET
    resp_assets = await client.get("/api/v1/catalog/assets", headers=auth_headers)
    assert resp_assets.status_code == 200
    assert len(resp_assets.json()) >= 2

    # 2. Get Asset Detail via GET
    resp_detail = await client.get(f"/api/v1/catalog/assets/{asset_id}", headers=auth_headers)
    assert resp_detail.status_code == 200
    assert resp_detail.json()["id"] == asset_id

    # 3. Get Lineage via GET
    resp_lineage = await client.get(f"/api/v1/catalog/lineage/{asset_id}", headers=auth_headers)
    assert resp_lineage.status_code == 200

    # 4. Get Glossary via GET
    resp_glossary = await client.get("/api/v1/catalog/glossary", headers=auth_headers)
    assert resp_glossary.status_code == 200
    assert len(resp_glossary.json()) >= 1

    # 5. Get Policies via GET
    resp_policies = await client.get("/api/v1/catalog/policies", headers=auth_headers)
    assert resp_policies.status_code == 200
    assert len(resp_policies.json()) >= 1
