"""
Sentinel AI — Enterprise Policy Engine REST Endpoints

Provides API routes for triggering policy suite evaluations, searching policy rule definitions,
and auditing compliance evaluation evidence.
"""

import datetime
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.session import get_async_session
from app.models.enums import PolicyCategory, PolicySeverity, PolicyStatus
from app.models.user import User
from app.services.policy_service import PolicyService

router = APIRouter(prefix="/policies", tags=["Enterprise Policy Engine & Rule Governance"])


# ── Pydantic Request & Response Schemas ────────────────────────────────────────
class PolicyDefinitionResponse(BaseModel):
    id: uuid.UUID
    policy_name: str
    category: PolicyCategory
    severity: PolicySeverity
    description: str
    rules_spec: dict[str, Any] | None = None
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class PolicyEvaluationResponse(BaseModel):
    id: uuid.UUID
    policy_id: uuid.UUID
    status: PolicyStatus
    severity: PolicySeverity
    evidence: dict[str, Any] | None = None
    recommendation: str
    evaluated_at: datetime.datetime
    policy_definition: PolicyDefinitionResponse | None = None

    class Config:
        from_attributes = True


class PolicyEvaluationRequest(BaseModel):
    target: dict[str, Any] = Field(default_factory=dict)


# ── REST API Routes ────────────────────────────────────────────────────────────
@router.post("/evaluate", response_model=list[PolicyEvaluationResponse], summary="Evaluate Enterprise Policies")
async def evaluate_policies(
    payload: PolicyEvaluationRequest = PolicyEvaluationRequest(),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Evaluate target payload across 10 enterprise Specification policy rules."""
    svc = PolicyService(db)
    return await svc.evaluate_policies(payload.target)


@router.get("", response_model=list[PolicyDefinitionResponse], summary="Get Policy Definitions")
async def get_policies(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve active enterprise policy definitions."""
    svc = PolicyService(db)
    return await svc.get_policies()


@router.get("/evaluations", response_model=list[PolicyEvaluationResponse], summary="Get Policy Evaluations")
async def get_policy_evaluations(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve recent policy evaluation compliance results."""
    svc = PolicyService(db)
    return await svc.get_evaluations()


@router.get("/{id}", response_model=PolicyDefinitionResponse, summary="Get Policy Detail")
async def get_policy_detail(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve detailed policy definition by UUID."""
    svc = PolicyService(db)
    policy = await svc.get_policy_detail(id)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy '{id}' not found",
        )
    return policy
