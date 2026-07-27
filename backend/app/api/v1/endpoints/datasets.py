"""
Sentinel AI — Datasets API Endpoints

Provides REST endpoints for dataset file uploads, database connection registration,
dataset listing, details retrieval, soft deletion, previews, schemas, and profiles.
"""

import os
import shutil
import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, get_db
from app.models.dataset import Dataset, DatasetColumn, DatasetSchema, DatasetVersion
from app.models.enums import ConnectorType, DatasetType
from app.repositories.dataset_repository import (
    DatasetColumnRepository,
    DatasetProfileRepository,
    DatasetRepository,
    DatasetSchemaRepository,
    DatasetVersionRepository,
)
from app.services.connector_service import ConnectorService
from app.services.profiling_service import ProfilingService

router = APIRouter(prefix="/datasets", tags=["Datasets"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    current_user: CurrentUser,
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str | None = Form(None),
    dataset_type: DatasetType = Form(DatasetType.SENSOR_STREAM),
    connector_type: ConnectorType = Form(ConnectorType.INDUSTRIAL_SENSOR),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Upload a dataset file (CSV/Sensor telemetry) and automatically profile & index schema."""
    dataset_repo = DatasetRepository(db)
    version_repo = DatasetVersionRepository(db)
    schema_repo = DatasetSchemaRepository(db)
    col_repo = DatasetColumnRepository(db)
    profile_repo = DatasetProfileRepository(db)

    # Save uploaded file
    file_id = uuid.uuid4().hex[:8]
    safe_filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)

    # Create Dataset record
    dataset = Dataset(
        name=name,
        description=description,
        dataset_type=dataset_type,
        connector_type=connector_type,
        connection_config={"file_path": file_path},
        owner_id=current_user.id,
    )
    dataset = await dataset_repo.create(dataset)

    # Create DatasetVersion record
    version = DatasetVersion(
        dataset_id=dataset.id,
        version_number=1,
        storage_path=file_path,
        file_size_bytes=file_size,
        ingested_by_id=current_user.id,
    )
    version = await version_repo.create(version)

    # Profile & discover schema
    profiling_svc = ProfilingService(profile_repository=profile_repo)
    connector_svc = ConnectorService()

    conn_type = connector_type if connector_type else ConnectorType.CSV
    config = {"file_path": file_path}

    schema_list = connector_svc.fetch_schema(conn_type, config)
    db_schema = DatasetSchema(dataset_version_id=version.id)
    db_schema = await schema_repo.create(db_schema)

    for idx, col_info in enumerate(schema_list):
        db_col = DatasetColumn(
            dataset_schema_id=db_schema.id,
            column_name=col_info["column_name"],
            data_type=col_info.get("data_type", "string"),
            position=idx,
            is_nullable=col_info.get("is_nullable", True),
            is_primary_key=col_info.get("is_primary_key", False),
        )
        await col_repo.create(db_col)

    # Generate profile
    profile = await profiling_svc.profile_and_persist(version.id, conn_type, config)
    await version_repo.update(version, {"row_count": profile.total_rows, "column_count": profile.total_columns})

    return {
        "message": "Dataset uploaded and indexed successfully",
        "dataset_id": str(dataset.id),
        "version_id": str(version.id),
        "total_rows": profile.total_rows,
        "total_columns": profile.total_columns,
    }


@router.post("/register-database", response_model=dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register_database(
    current_user: CurrentUser,
    name: str = Form(...),
    connector_type: ConnectorType = Form(ConnectorType.POSTGRESQL),
    host: str = Form(...),
    port: int = Form(5432),
    database_name: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    table_name: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Register an external database table as a dataset source."""
    dataset_repo = DatasetRepository(db)
    version_repo = DatasetVersionRepository(db)

    config = {
        "host": host,
        "port": port,
        "database": database_name,
        "username": username,
        "password": password,
        "table_name": table_name,
    }

    dataset = Dataset(
        name=name,
        description=f"Database table: {database_name}.{table_name}",
        dataset_type=DatasetType.TABULAR,
        connector_type=connector_type,
        connection_config=config,
        owner_id=current_user.id,
    )
    dataset = await dataset_repo.create(dataset)

    version = DatasetVersion(
        dataset_id=dataset.id,
        version_number=1,
        storage_path=f"{database_name}.{table_name}",
        ingested_by_id=current_user.id,
    )
    version = await version_repo.create(version)

    return {
        "message": "Database connector registered successfully",
        "dataset_id": str(dataset.id),
        "version_id": str(version.id),
    }


@router.get("", response_model=dict[str, Any])
async def list_datasets(
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    query: str | None = Query(None),
    dataset_type: DatasetType | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List datasets with pagination, filtering, search, and sorting."""
    dataset_repo = DatasetRepository(db)
    offset = (page - 1) * limit
    items, total = await dataset_repo.get_datasets_paginated(
        offset=offset,
        limit=limit,
        search=query,
    )

    dataset_list = []
    for d in items:
        active_version_id = str(d.versions[0].id) if d.versions else None
        dataset_list.append({
            "id": str(d.id),
            "name": d.name,
            "description": d.description,
            "dataset_type": d.dataset_type.value if hasattr(d.dataset_type, "value") else str(d.dataset_type),
            "connector_type": d.connector_type.value if hasattr(d.connector_type, "value") else str(d.connector_type),
            "is_active": d.is_active,
            "active_version_id": active_version_id,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        })

    return {
        "items": dataset_list,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if limit > 0 else 1,
    }


@router.get("/{dataset_id}", response_model=dict[str, Any])
async def get_dataset(
    dataset_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get dataset details by ID."""
    dataset_repo = DatasetRepository(db)
    dataset = await dataset_repo.get_by_id_with_relations(dataset_id)
    if not dataset or not dataset.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    active_version = dataset.versions[0] if dataset.versions else None

    return {
        "id": str(dataset.id),
        "name": dataset.name,
        "description": dataset.description,
        "dataset_type": dataset.dataset_type.value if hasattr(dataset.dataset_type, "value") else str(dataset.dataset_type),
        "connector_type": dataset.connector_type.value if hasattr(dataset.connector_type, "value") else str(dataset.connector_type),
        "connection_config": dataset.connection_config,
        "is_active": dataset.is_active,
        "active_version": {
            "id": str(active_version.id),
            "version_number": active_version.version_number,
            "storage_path": active_version.storage_path,
            "row_count": active_version.row_count,
            "column_count": active_version.column_count,
            "created_at": active_version.created_at.isoformat() if active_version.created_at else None,
        } if active_version else None,
        "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
    }


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft delete a dataset."""
    dataset_repo = DatasetRepository(db)
    dataset = await dataset_repo.get_by_id(dataset_id)
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    await dataset_repo.update(dataset, {"is_active": False})


@router.get("/{dataset_id}/preview", response_model=dict[str, Any])
async def get_dataset_preview(
    dataset_id: uuid.UUID,
    current_user: CurrentUser,
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get preview rows from the active version of a dataset."""
    dataset_repo = DatasetRepository(db)
    connector_svc = ConnectorService()

    dataset = await dataset_repo.get_by_id_with_relations(dataset_id)
    if not dataset or not dataset.versions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset version not found")

    version = dataset.versions[0]
    config = {"file_path": version.storage_path}
    rows = connector_svc.preview_dataset(dataset.connector_type, config, limit=limit)

    return {
        "dataset_id": str(dataset.id),
        "version_id": str(version.id),
        "limit": limit,
        "rows": rows,
    }


@router.get("/{dataset_id}/schema", response_model=dict[str, Any])
async def get_dataset_schema(
    dataset_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get column schema definition for the active version of a dataset."""
    dataset_repo = DatasetRepository(db)
    connector_svc = ConnectorService()

    dataset = await dataset_repo.get_by_id_with_relations(dataset_id)
    if not dataset or not dataset.versions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset version not found")

    version = dataset.versions[0]
    config = {"file_path": version.storage_path}
    schema = connector_svc.fetch_schema(dataset.connector_type, config)

    return {
        "dataset_id": str(dataset.id),
        "version_id": str(version.id),
        "columns": schema,
    }


@router.get("/{dataset_id}/profile", response_model=dict[str, Any])
async def get_dataset_profile(
    dataset_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get statistical profile and automated insights for the active version of a dataset."""
    dataset_repo = DatasetRepository(db)
    profile_repo = DatasetProfileRepository(db)
    profiling_svc = ProfilingService(profile_repository=profile_repo)

    dataset = await dataset_repo.get_by_id_with_relations(dataset_id)
    if not dataset or not dataset.versions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset version not found")

    version = dataset.versions[0]

    db_profile = await profile_repo.get_by_version_id(version.id)
    if db_profile and db_profile.profile_data:
        return {
            "dataset_id": str(dataset.id),
            "version_id": str(version.id),
            "profile": db_profile.profile_data,
        }

    config = {"file_path": version.storage_path}
    profile = await profiling_svc.profile_and_persist(
        version.id, dataset.connector_type, config
    )
    return {
        "dataset_id": str(dataset.id),
        "version_id": str(version.id),
        "profile": profile.profile_data,
    }
