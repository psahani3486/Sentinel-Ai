"""
Sentinel AI — Dataset Schemas

Pydantic v2 schemas for Datasets, Versions, Schemas, Columns, and Profiles.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ConnectorType, DatasetType


# ── Column Schemas ────────────────────────────────────────────────────────────

class DatasetColumnBase(BaseModel):
    column_name: str = Field(..., max_length=255)
    data_type: str = Field(..., max_length=64)
    is_nullable: bool = True
    is_primary_key: bool = False
    position: int = Field(..., ge=0)
    sample_values: list[Any] | None = None


class DatasetColumnCreate(DatasetColumnBase):
    pass


class DatasetColumnResponse(DatasetColumnBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_schema_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ── Schema Header Schemas ─────────────────────────────────────────────────────

class DatasetSchemaBase(BaseModel):
    column_count: int = Field(default=0, ge=0)


class DatasetSchemaCreate(DatasetSchemaBase):
    columns: list[DatasetColumnCreate] = []


class DatasetSchemaResponse(DatasetSchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_version_id: uuid.UUID
    columns: list[DatasetColumnResponse] = []
    created_at: datetime
    updated_at: datetime


# ── Profile Schemas ───────────────────────────────────────────────────────────

class DatasetProfileBase(BaseModel):
    total_rows: int = Field(..., ge=0)
    total_columns: int = Field(..., ge=0)
    memory_bytes: int = Field(..., ge=0)
    profile_data: dict[str, Any]


class DatasetProfileCreate(DatasetProfileBase):
    dataset_version_id: uuid.UUID


class DatasetProfileResponse(DatasetProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_version_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ── Version Schemas ───────────────────────────────────────────────────────────

class DatasetVersionBase(BaseModel):
    storage_path: str = Field(..., max_length=512)
    row_count: int = Field(default=0, ge=0)
    column_count: int = Field(default=0, ge=0)
    file_size_bytes: int = Field(default=0, ge=0)
    checksum: str | None = Field(default=None, max_length=64)


class DatasetVersionCreate(DatasetVersionBase):
    version_number: int = Field(default=1, ge=1)


class DatasetVersionResponse(DatasetVersionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_id: uuid.UUID
    version_number: int
    ingested_by_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


# ── Dataset Core Schemas ──────────────────────────────────────────────────────

class DatasetBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    dataset_type: DatasetType = DatasetType.TABULAR
    connector_type: ConnectorType = ConnectorType.CSV
    connection_config: dict[str, Any] | None = None


class DatasetCreate(DatasetBase):
    pass


class DatasetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    dataset_type: DatasetType | None = None
    connector_type: ConnectorType | None = None
    connection_config: dict[str, Any] | None = None
    is_active: bool | None = None


class DatasetSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None = None
    dataset_type: DatasetType
    connector_type: ConnectorType
    owner_id: uuid.UUID
    is_active: bool
    version_count: int = 0
    latest_version_number: int | None = None
    latest_row_count: int | None = None
    created_at: datetime
    updated_at: datetime


class DatasetResponse(DatasetBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    latest_version: DatasetVersionResponse | None = None
