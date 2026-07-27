"""
Sentinel AI — Validation Schemas

Pydantic v2 schemas for Validation Rules, Validation Runs, and Validation Results.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RuleType, RunStatus, ValidationSeverity, ValidationStatus


# ── Rule Schemas ──────────────────────────────────────────────────────────────

class ValidationRuleBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    rule_type: RuleType
    description: str | None = None
    severity: ValidationSeverity = ValidationSeverity.MEDIUM
    parameters: dict[str, Any] | None = None
    is_active: bool = True


class ValidationRuleCreate(ValidationRuleBase):
    pass


class ValidationRuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    severity: ValidationSeverity | None = None
    parameters: dict[str, Any] | None = None
    is_active: bool | None = None


class ValidationRuleResponse(ValidationRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ── Result Schemas ────────────────────────────────────────────────────────────

class ValidationResultBase(BaseModel):
    rule_type: RuleType
    status: ValidationStatus
    severity: ValidationSeverity
    message: str
    affected_columns: list[str] | None = None
    affected_rows_count: int = Field(default=0, ge=0)
    execution_time_ms: float = Field(default=0.0, ge=0.0)
    score_impact: float = Field(default=0.0, ge=0.0)
    details: dict[str, Any] | None = None


class ValidationResultCreate(ValidationResultBase):
    rule_id: uuid.UUID | None = None


class ValidationResultResponse(ValidationResultBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    validation_run_id: uuid.UUID
    rule_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


# ── Run Schemas ───────────────────────────────────────────────────────────────

class ValidationRunBase(BaseModel):
    dataset_id: uuid.UUID
    dataset_version_id: uuid.UUID


class ValidationRunCreate(ValidationRunBase):
    pass


class ValidationRunSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dataset_id: uuid.UUID
    dataset_version_id: uuid.UUID
    status: RunStatus
    overall_score: float | None = None
    completeness_score: float | None = None
    consistency_score: float | None = None
    accuracy_score: float | None = None
    freshness_score: float | None = None
    execution_time_ms: float
    passed_rules_count: int = 0
    warning_rules_count: int = 0
    failed_rules_count: int = 0
    created_at: datetime


class ValidationRunResponse(ValidationRunBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: RunStatus
    overall_score: float | None = None
    completeness_score: float | None = None
    consistency_score: float | None = None
    accuracy_score: float | None = None
    freshness_score: float | None = None
    execution_time_ms: float
    triggered_by_id: uuid.UUID | None = None
    results: list[ValidationResultResponse] = []
    created_at: datetime
    updated_at: datetime
