"""
Sentinel AI — Validation API Endpoints

Provides REST endpoints to trigger dataset validation runs, retrieve validation history,
inspect validation run details & rule failure diagnostics, and list registered validation rules.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, get_db
from app.repositories.dataset_repository import DatasetRepository, DatasetVersionRepository
from app.repositories.validation_repository import (
    ValidationResultRepository,
    ValidationRunRepository,
)
from app.services.validation_service import ValidationService
from app.validation_engine.registry import RuleRegistry

router = APIRouter(tags=["Validation"])


@router.post("/datasets/{dataset_id}/validate", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
async def trigger_dataset_validation(
    dataset_id: uuid.UUID,
    current_user: CurrentUser,
    rules: list[dict[str, Any]] | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Trigger a validation engine run for the active version of a dataset."""
    dataset_repo = DatasetRepository(db)
    version_repo = DatasetVersionRepository(db)
    run_repo = ValidationRunRepository(db)
    res_repo = ValidationResultRepository(db)

    dataset = await dataset_repo.get_by_id_with_relations(dataset_id)
    if not dataset or not dataset.versions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset active version not found")

    version = dataset.versions[0]
    val_svc = ValidationService(
        run_repository=run_repo,
        result_repository=res_repo,
        version_repository=version_repo,
    )

    config = {"file_path": version.storage_path}
    db_run = await val_svc.run_and_persist(
        version.id, dataset.connector_type, config, rules=rules
    )

    return {
        "message": "Validation run completed and persisted successfully",
        "validation_run_id": str(db_run.id),
        "status": db_run.status.value if hasattr(db_run.status, "value") else str(db_run.status),
        "overall_score": db_run.overall_score,
        "execution_time_ms": db_run.execution_time_ms,
    }


@router.get("/datasets/{dataset_id}/validation-history", response_model=dict[str, Any])
async def get_dataset_validation_history(
    dataset_id: uuid.UUID,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve historical validation runs for a dataset."""
    dataset_repo = DatasetRepository(db)
    run_repo = ValidationRunRepository(db)

    dataset = await dataset_repo.get_by_id(dataset_id)
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    offset = (page - 1) * limit
    runs, total = await run_repo.get_runs_by_dataset(dataset_id, offset=offset, limit=limit)

    history_list = []
    for r in runs:
        history_list.append({
            "id": str(r.id),
            "dataset_version_id": str(r.dataset_version_id),
            "status": r.status.value if hasattr(r.status, "value") else str(r.status),
            "overall_score": r.overall_score,
            "completeness_score": r.completeness_score,
            "consistency_score": r.consistency_score,
            "accuracy_score": r.accuracy_score,
            "freshness_score": r.freshness_score,
            "execution_time_ms": r.execution_time_ms,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })

    return {
        "dataset_id": str(dataset_id),
        "items": history_list,
        "total": total,
        "page": page,
        "limit": limit,
    }


@router.get("/validations/{validation_id}", response_model=dict[str, Any])
async def get_validation_details(
    validation_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get detailed results for a specific validation run."""
    run_repo = ValidationRunRepository(db)
    res_repo = ValidationResultRepository(db)

    run = await run_repo.get_by_id(validation_id)
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validation run not found")

    results = await res_repo.get_results_by_run_id(validation_id)
    res_list = []

    for r in results:
        res_list.append({
            "id": str(r.id),
            "rule_type": r.rule_type.value if hasattr(r.rule_type, "value") else str(r.rule_type),
            "status": r.status.value if hasattr(r.status, "value") else str(r.status),
            "severity": r.severity.value if hasattr(r.severity, "value") else str(r.severity),
            "message": r.message,
            "affected_columns": r.affected_columns,
            "affected_rows_count": r.affected_rows_count,
            "execution_time_ms": r.execution_time_ms,
            "score_impact": r.score_impact,
            "details": r.details,
        })

    return {
        "id": str(run.id),
        "dataset_id": str(run.dataset_id),
        "dataset_version_id": str(run.dataset_version_id),
        "status": run.status.value if hasattr(run.status, "value") else str(run.status),
        "overall_score": run.overall_score,
        "completeness_score": run.completeness_score,
        "consistency_score": run.consistency_score,
        "accuracy_score": run.accuracy_score,
        "freshness_score": run.freshness_score,
        "execution_time_ms": run.execution_time_ms,
        "results": res_list,
        "created_at": run.created_at.isoformat() if run.created_at else None,
    }


@router.get("/validation-rules", response_model=dict[str, Any])
async def list_validation_rules(
    current_user: CurrentUser,
) -> dict[str, Any]:
    """List all registered validation rules and metadata."""
    supported_keys = RuleRegistry.list_supported_rules()
    rule_metadata_list = []

    for key in supported_keys:
        rule_cls = RuleRegistry.get(key)
        dummy = rule_cls()
        rule_metadata_list.append({
            "rule_type": dummy.rule_type.value if hasattr(dummy.rule_type, "value") else str(dummy.rule_type),
            "name": dummy.name,
            "description": dummy.description,
            "category": dummy.category.value if hasattr(dummy.category, "value") else str(dummy.category),
            "severity": dummy.severity.value if hasattr(dummy.severity, "value") else str(dummy.severity),
        })

    return {
        "total_rules": len(rule_metadata_list),
        "rules": rule_metadata_list,
    }
