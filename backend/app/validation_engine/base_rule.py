"""
Sentinel AI — Base Validation Rule & Result Model

Defines the abstract interface for all validation rules, the RuleCategory enumeration,
and the structured RuleResult model returned by every rule execution.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import RuleType, ValidationSeverity, ValidationStatus


class RuleCategory(str, Enum):
    """Categories for classifying data quality rules."""

    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    ACCURACY = "accuracy"
    FRESHNESS = "freshness"
    SCHEMA = "schema"
    STATISTICAL = "statistical"
    BUSINESS = "business"


class RuleResult(BaseModel):
    """Structured result returned by every validation rule execution."""

    rule_name: str
    rule_type: RuleType | str
    category: RuleCategory
    status: ValidationStatus
    severity: ValidationSeverity
    message: str
    affected_columns: list[str] = Field(default_factory=list)
    affected_rows_count: int = 0
    execution_time_ms: float = 0.0
    score_impact: float = 0.0
    details: dict[str, Any] = Field(default_factory=dict)


class BaseValidationRule(ABC):
    """Abstract Base Class for all Sentinel AI validation rules."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config: dict[str, Any] = config or {}

    @abstractmethod
    def validate(
        self,
        df: Any,  # pandas DataFrame
        schema_info: list[dict[str, Any]] | None = None,
        history: list[dict[str, Any]] | None = None,
    ) -> RuleResult:
        """
        Execute the validation logic against a dataset.

        Args:
            df: The pandas DataFrame payload to validate.
            schema_info: Discovered schema metadata if available.
            history: Historical validation results for temporal comparisons.

        Returns:
            RuleResult detailing status, message, affected columns/rows, and metadata.
        """
        pass

    @property
    @abstractmethod
    def rule_type(self) -> RuleType:
        """Return the unique RuleType identifier."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return human-readable rule name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return rule description."""
        pass

    @property
    @abstractmethod
    def severity(self) -> ValidationSeverity:
        """Return rule default severity level."""
        pass

    @property
    @abstractmethod
    def category(self) -> RuleCategory:
        """Return rule category classification."""
        pass

    def required_columns(self) -> list[str]:
        """Return list of column names required by this rule config."""
        cols = self.config.get("columns") or self.config.get("column")
        if isinstance(cols, str):
            return [cols]
        elif isinstance(cols, list):
            return [str(c) for c in cols]
        return []

    def configuration(self) -> dict[str, Any]:
        """Return the rule configuration parameters."""
        return self.config
