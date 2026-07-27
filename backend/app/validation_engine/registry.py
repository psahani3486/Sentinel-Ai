"""
Sentinel AI — Rule Registry

Dynamic registry mapping RuleType identifiers to concrete BaseValidationRule classes.
Eliminates switch statements and large if-else chains. Supports custom rule registration.
"""

import logging
from typing import Any, Type

from app.core.exceptions import ConfigurationError
from app.models.enums import RuleType
from app.validation_engine.base_rule import BaseValidationRule, RuleCategory
from app.validation_engine.rules import (
    ColumnStatisticsRule,
    ConstantColumnRule,
    CrossColumnBusinessRule,
    DataAccuracyRule,
    DataCompletenessRule,
    DataConsistencyRule,
    DuplicateColumnRule,
    DuplicateRowsRule,
    FreshnessRule,
    HighCardinalityRule,
    InvalidNumericRule,
    InvalidTimestampRule,
    LowCardinalityRule,
    MissingValuesRule,
    NegativeSensorValueRule,
    NullColumnRule,
    OutlierRule,
    PrimaryKeyRule,
    SchemaChangeRule,
    SensorRangeRule,
    UniqueConstraintRule,
    WrongDataTypeRule,
)

logger = logging.getLogger(__name__)


class RuleRegistry:
    """Registry managing validation rule registration and dynamic instantiation."""

    _registry: dict[RuleType | str, Type[BaseValidationRule]] = {}

    @classmethod
    def register(
        cls, rule_type: RuleType | str, rule_cls: Type[BaseValidationRule]
    ) -> None:
        """Register a new validation rule class under a given RuleType."""
        key = rule_type.value if isinstance(rule_type, RuleType) else str(rule_type).lower()
        cls._registry[key] = rule_cls
        logger.debug("Registered validation rule: '%s' -> %s", key, rule_cls.__name__)

    @classmethod
    def get(cls, rule_type: RuleType | str) -> Type[BaseValidationRule]:
        """Retrieve rule class by RuleType or string identifier."""
        key = rule_type.value if isinstance(rule_type, RuleType) else str(rule_type).lower()
        if key not in cls._registry:
            raise ConfigurationError(
                f"Unsupported validation rule_type '{rule_type}'. Supported rules: {cls.list_supported_rules()}"
            )
        return cls._registry[key]

    @classmethod
    def create(
        cls, rule_type: RuleType | str, config: dict[str, Any] | None = None
    ) -> BaseValidationRule:
        """Instantiate a validation rule with configuration parameters."""
        rule_cls = cls.get(rule_type)
        return rule_cls(config=config)

    @classmethod
    def list_supported_rules(cls) -> list[str]:
        """Return list of all registered rule_type identifiers."""
        return list(cls._registry.keys())

    @classmethod
    def get_rules_by_category(cls, category: RuleCategory | str) -> list[Type[BaseValidationRule]]:
        """Return rule classes belonging to a specific RuleCategory."""
        cat_str = category.value if isinstance(category, RuleCategory) else str(category).lower()
        matched = []
        for rule_cls in cls._registry.values():
            dummy = rule_cls()
            if dummy.category.value == cat_str:
                matched.append(rule_cls)
        return matched


# Automatically register the 21 default validation rules
RuleRegistry.register(RuleType.MISSING_VALUES, MissingValuesRule)
RuleRegistry.register(RuleType.NULL_COLUMNS, NullColumnRule)
RuleRegistry.register(RuleType.DATA_COMPLETENESS, DataCompletenessRule)
RuleRegistry.register(RuleType.DUPLICATE_ROWS, DuplicateRowsRule)
RuleRegistry.register(RuleType.DUPLICATE_COLUMNS, DuplicateColumnRule)
RuleRegistry.register(RuleType.DATA_CONSISTENCY, DataConsistencyRule)
RuleRegistry.register(RuleType.INVALID_NUMERIC_VALUES, InvalidNumericRule)
RuleRegistry.register(RuleType.NEGATIVE_SENSOR_VALUES, NegativeSensorValueRule)
RuleRegistry.register(RuleType.INVALID_SENSOR_RANGE, SensorRangeRule)
RuleRegistry.register(RuleType.DATA_ACCURACY, DataAccuracyRule)
RuleRegistry.register(RuleType.INVALID_TIMESTAMPS, InvalidTimestampRule)
RuleRegistry.register(RuleType.FRESHNESS_VALIDATION, FreshnessRule)
RuleRegistry.register(RuleType.WRONG_DATA_TYPES, WrongDataTypeRule)
RuleRegistry.register(RuleType.SCHEMA_CHANGES, SchemaChangeRule)
RuleRegistry.register(RuleType.PRIMARY_KEY_VALIDATION, PrimaryKeyRule)
RuleRegistry.register(RuleType.UNIQUE_CONSTRAINT_VALIDATION, UniqueConstraintRule)
RuleRegistry.register(RuleType.OUTLIERS, OutlierRule)
RuleRegistry.register(RuleType.CONSTANT_COLUMNS, ConstantColumnRule)
RuleRegistry.register(RuleType.HIGH_CARDINALITY, HighCardinalityRule)
RuleRegistry.register(RuleType.LOW_CARDINALITY, LowCardinalityRule)
RuleRegistry.register(RuleType.COLUMN_STATISTICS, ColumnStatisticsRule)
RuleRegistry.register(RuleType.BUSINESS_RULE, CrossColumnBusinessRule)
