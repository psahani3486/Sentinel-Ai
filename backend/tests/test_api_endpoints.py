"""
Sentinel AI — Phase 2E REST API Endpoints Integration Tests

Verifies dataset uploading, listing, details, previews, schema, profile,
validation execution, history, validation details, and rule listing APIs.
"""

import os
import pytest
from httpx import AsyncClient


@pytest.fixture
def sample_ai4i_file() -> str:
    """Return path to sample AI4I 2020 dataset file."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "data", "samples", "ai4i2020.csv")


@pytest.mark.asyncio
async def test_validation_rules_endpoint(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """Test GET /api/v1/validation-rules endpoint."""
    response = await client.get("/api/v1/validation-rules", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "rules" in data
    assert data["total_rules"] == 22


@pytest.mark.asyncio
async def test_dataset_upload_and_lifecycle(
    client: AsyncClient, auth_headers: dict[str, str], sample_ai4i_file: str
) -> None:
    """Test dataset upload endpoint, dataset listing, details, preview, schema, and profile endpoints."""

    # 1. Upload dataset file
    with open(sample_ai4i_file, "rb") as f:
        files = {"file": ("ai4i2020.csv", f, "text/csv")}
        data = {
            "name": "API Test AI4I Dataset",
            "description": "Uploaded via REST API test",
            "dataset_type": "sensor_stream",
            "connector_type": "industrial_sensor",
        }
        upload_res = await client.post(
            "/api/v1/datasets/upload", files=files, data=data, headers=auth_headers
        )

    assert upload_res.status_code == 201
    upload_data = upload_res.json()
    dataset_id = upload_data["dataset_id"]
    assert dataset_id is not None

    # 2. List datasets
    list_res = await client.get("/api/v1/datasets?page=1&limit=10", headers=auth_headers)
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert any(d["id"] == dataset_id for d in list_data["items"])

    # 3. Get dataset details
    detail_res = await client.get(f"/api/v1/datasets/{dataset_id}", headers=auth_headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["name"] == "API Test AI4I Dataset"
    assert detail_data["active_version"] is not None

    # 4. Get preview
    preview_res = await client.get(f"/api/v1/datasets/{dataset_id}/preview?limit=5", headers=auth_headers)
    assert preview_res.status_code == 200
    preview_data = preview_res.json()
    assert len(preview_data["rows"]) == 5

    # 5. Get schema
    schema_res = await client.get(f"/api/v1/datasets/{dataset_id}/schema", headers=auth_headers)
    assert schema_res.status_code == 200
    schema_data = schema_res.json()
    assert len(schema_data["columns"]) > 0

    # 6. Get profile
    profile_res = await client.get(f"/api/v1/datasets/{dataset_id}/profile", headers=auth_headers)
    assert profile_res.status_code == 200
    profile_data = profile_res.json()
    assert "profile" in profile_data

    # 7. Trigger validation
    val_res = await client.post(f"/api/v1/datasets/{dataset_id}/validate", headers=auth_headers)
    assert val_res.status_code == 201
    val_data = val_res.json()
    validation_run_id = val_data["validation_run_id"]
    assert validation_run_id is not None

    # 8. Get dataset validation history
    hist_res = await client.get(f"/api/v1/datasets/{dataset_id}/validation-history", headers=auth_headers)
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert hist_data["total"] >= 1

    # 9. Get validation details
    val_detail_res = await client.get(f"/api/v1/validations/{validation_run_id}", headers=auth_headers)
    assert val_detail_res.status_code == 200
    val_detail_data = val_detail_res.json()
    assert val_detail_data["id"] == validation_run_id
    assert "results" in val_detail_data

    # 10. Soft delete dataset
    del_res = await client.delete(f"/api/v1/datasets/{dataset_id}", headers=auth_headers)
    assert del_res.status_code == 204
