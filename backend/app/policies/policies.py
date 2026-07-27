"""
Sentinel AI — Built-in Enterprise Policies

Implements 10 concrete Specification Pattern policy rules:
1. Dataset Governance Policy
2. Schema Policy
3. Validation Policy
4. Quality Threshold Policy
5. Drift Threshold Policy
6. Workflow Policy
7. Plugin Policy
8. Catalog Governance Policy
9. Retention Policy
10. Incident Escalation Policy
"""

from typing import Any

from app.models.enums import PolicyCategory, PolicySeverity, PolicyStatus
from app.policies.base_policy import BasePolicy, PolicyResult


class DatasetGovernancePolicy(BasePolicy):
    @property
    def policy_id(self) -> str:
        return "pol-dataset-gov-01"

    @property
    def policy_name(self) -> str:
        return "Dataset Mandatory Ownership Governance Policy"

    @property
    def category(self) -> PolicyCategory:
        return PolicyCategory.DATASET_GOVERNANCE

    @property
    def severity(self) -> PolicySeverity:
        return PolicySeverity.HIGH

    def is_satisfied_by(self, target: dict[str, Any]) -> bool:
        return bool(target.get("owner")) and bool(target.get("steward"))

    def evaluate(self, target: dict[str, Any]) -> PolicyResult:
        satisfied = self.is_satisfied_by(target)
        status = PolicyStatus.PASS if satisfied else PolicyStatus.FAIL
        return PolicyResult(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            category=self.category,
            status=status,
            severity=self.severity,
            evidence={"owner": target.get("owner"), "steward": target.get("steward")},
            recommendation="No action required." if satisfied else "Assign dataset owner and steward in catalog.",
        )


class SchemaPolicy(BasePolicy):
    @property
    def policy_id(self) -> str:
        return "pol-schema-02"

    @property
    def policy_name(self) -> str:
        return "Zero Breaking Schema Changes Policy"

    @property
    def category(self) -> PolicyCategory:
        return PolicyCategory.SCHEMA

    @property
    def severity(self) -> PolicySeverity:
        return PolicySeverity.CRITICAL

    def is_satisfied_by(self, target: dict[str, Any]) -> bool:
        return not bool(target.get("dropped_columns", []))

    def evaluate(self, target: dict[str, Any]) -> PolicyResult:
        satisfied = self.is_satisfied_by(target)
        status = PolicyStatus.PASS if satisfied else PolicyStatus.FAIL
        return PolicyResult(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            category=self.category,
            status=status,
            severity=self.severity,
            evidence={"dropped_columns": target.get("dropped_columns", [])},
            recommendation="No action required." if satisfied else "Revert dropped columns or update downstream schemas.",
        )


class ValidationPolicy(BasePolicy):
    @property
    def policy_id(self) -> str:
        return "pol-validation-03"

    @property
    def policy_name(self) -> str:
        return "Critical Quality Contract Execution Policy"

    @property
    def category(self) -> PolicyCategory:
        return PolicyCategory.VALIDATION

    @property
    def severity(self) -> PolicySeverity:
        return PolicySeverity.HIGH

    def is_satisfied_by(self, target: dict[str, Any]) -> bool:
        return target.get("critical_failed_count", 0) == 0

    def evaluate(self, target: dict[str, Any]) -> PolicyResult:
        satisfied = self.is_satisfied_by(target)
        status = PolicyStatus.PASS if satisfied else PolicyStatus.FAIL
        return PolicyResult(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            category=self.category,
            status=status,
            severity=self.severity,
            evidence={"critical_failed_count": target.get("critical_failed_count", 0)},
            recommendation="No action required." if satisfied else "Investigate critical contract failures.",
        )


class QualityThresholdPolicy(BasePolicy):
    @property
    def policy_id(self) -> str:
        return "pol-quality-04"

    @property
    def policy_name(self) -> str:
        return "Minimum 90% Quality Score Policy"

    @property
    def category(self) -> PolicyCategory:
        return PolicyCategory.QUALITY_THRESHOLD

    @property
    def severity(self) -> PolicySeverity:
        return PolicySeverity.HIGH

    def is_satisfied_by(self, target: dict[str, Any]) -> bool:
        return target.get("quality_score", 100.0) >= 90.0

    def evaluate(self, target: dict[str, Any]) -> PolicyResult:
        score = target.get("quality_score", 100.0)
        satisfied = self.is_satisfied_by(target)
        status = PolicyStatus.PASS if satisfied else (PolicyStatus.WARNING if score >= 80.0 else PolicyStatus.FAIL)
        return PolicyResult(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            category=self.category,
            status=status,
            severity=self.severity,
            evidence={"quality_score": score, "threshold": 90.0},
            recommendation="No action required." if satisfied else "Remediate failing validation rules to boost quality score.",
        )


class DriftThresholdPolicy(BasePolicy):
    @property
    def policy_id(self) -> str:
        return "pol-drift-05"

    @property
    def policy_name(self) -> str:
        return "PSI Feature Distribution Drift Boundary Policy"

    @property
    def category(self) -> PolicyCategory:
        return PolicyCategory.DRIFT_THRESHOLD

    @property
    def severity(self) -> PolicySeverity:
        return PolicySeverity.MEDIUM

    def is_satisfied_by(self, target: dict[str, Any]) -> bool:
        return target.get("max_psi", 0.0) < 0.25

    def evaluate(self, target: dict[str, Any]) -> PolicyResult:
        psi = target.get("max_psi", 0.0)
        satisfied = self.is_satisfied_by(target)
        status = PolicyStatus.PASS if satisfied else PolicyStatus.WARNING
        return PolicyResult(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            category=self.category,
            status=status,
            severity=self.severity,
            evidence={"max_psi": psi, "boundary": 0.25},
            recommendation="No action required." if satisfied else "Retrain baseline distribution model.",
        )


class WorkflowPolicy(BasePolicy):
    @property
    def policy_id(self) -> str:
        return "pol-workflow-06"

    @property
    def policy_name(self) -> str:
        return "Workflow Maximum Execution SLA Policy"

    @property
    def category(self) -> PolicyCategory:
        return PolicyCategory.WORKFLOW

    @property
    def severity(self) -> PolicySeverity:
        return PolicySeverity.MEDIUM

    def is_satisfied_by(self, target: dict[str, Any]) -> bool:
        return target.get("duration_seconds", 0) <= 300

    def evaluate(self, target: dict[str, Any]) -> PolicyResult:
        dur = target.get("duration_seconds", 0)
        satisfied = self.is_satisfied_by(target)
        status = PolicyStatus.PASS if satisfied else PolicyStatus.WARNING
        return PolicyResult(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            category=self.category,
            status=status,
            severity=self.severity,
            evidence={"duration_seconds": dur, "max_sla_seconds": 300},
            recommendation="No action required." if satisfied else "Optimize slow pipeline step DAG nodes.",
        )


class PluginPolicy(BasePolicy):
    @property
    def policy_id(self) -> str:
        return "pol-plugin-07"

    @property
    def policy_name(self) -> str:
        return "Local Plugin Extension Security Sandboxing Policy"

    @property
    def category(self) -> PolicyCategory:
        return PolicyCategory.PLUGIN

    @property
    def severity(self) -> PolicySeverity:
        return PolicySeverity.HIGH

    def is_satisfied_by(self, target: dict[str, Any]) -> bool:
        perms = target.get("permissions", [])
        return "root_access" not in perms

    def evaluate(self, target: dict[str, Any]) -> PolicyResult:
        satisfied = self.is_satisfied_by(target)
        status = PolicyStatus.PASS if satisfied else PolicyStatus.FAIL
        return PolicyResult(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            category=self.category,
            status=status,
            severity=self.severity,
            evidence={"permissions": target.get("permissions", [])},
            recommendation="No action required." if satisfied else "Remove elevated root access permission from plugin manifest.",
        )


class CatalogGovernancePolicy(BasePolicy):
    @property
    def policy_id(self) -> str:
        return "pol-catalog-08"

    @property
    def policy_name(self) -> str:
        return "Data Classification Sensitivity Tier Policy"

    @property
    def category(self) -> PolicyCategory:
        return PolicyCategory.CATALOG_GOVERNANCE

    @property
    def severity(self) -> PolicySeverity:
        return PolicySeverity.HIGH

    def is_satisfied_by(self, target: dict[str, Any]) -> bool:
        return target.get("sensitivity") in ["public", "internal", "confidential", "restricted", "pii"]

    def evaluate(self, target: dict[str, Any]) -> PolicyResult:
        satisfied = self.is_satisfied_by(target)
        status = PolicyStatus.PASS if satisfied else PolicyStatus.FAIL
        return PolicyResult(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            category=self.category,
            status=status,
            severity=self.severity,
            evidence={"sensitivity": target.get("sensitivity")},
            recommendation="No action required." if satisfied else "Assign valid security sensitivity tier.",
        )


class RetentionPolicy(BasePolicy):
    @property
    def policy_id(self) -> str:
        return "pol-retention-09"

    @property
    def policy_name(self) -> str:
        return "GDPR Data Retention Compliance Policy"

    @property
    def category(self) -> PolicyCategory:
        return PolicyCategory.RETENTION

    @property
    def severity(self) -> PolicySeverity:
        return PolicySeverity.CRITICAL

    def is_satisfied_by(self, target: dict[str, Any]) -> bool:
        return target.get("retention_days", 365) <= 365

    def evaluate(self, target: dict[str, Any]) -> PolicyResult:
        ret = target.get("retention_days", 365)
        satisfied = self.is_satisfied_by(target)
        status = PolicyStatus.PASS if satisfied else PolicyStatus.FAIL
        return PolicyResult(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            category=self.category,
            status=status,
            severity=self.severity,
            evidence={"retention_days": ret, "max_allowed_days": 365},
            recommendation="No action required." if satisfied else "Reduce retention period to 365 days for GDPR compliance.",
        )


class IncidentEscalationPolicy(BasePolicy):
    @property
    def policy_id(self) -> str:
        return "pol-incident-10"

    @property
    def policy_name(self) -> str:
        return "Critical Incident Automated Escalation SLA Policy"

    @property
    def category(self) -> PolicyCategory:
        return PolicyCategory.INCIDENT_ESCALATION

    @property
    def severity(self) -> PolicySeverity:
        return PolicySeverity.CRITICAL

    def is_satisfied_by(self, target: dict[str, Any]) -> bool:
        if target.get("severity") == "critical":
            return target.get("open_hours", 0) <= 2
        return True

    def evaluate(self, target: dict[str, Any]) -> PolicyResult:
        satisfied = self.is_satisfied_by(target)
        status = PolicyStatus.PASS if satisfied else PolicyStatus.FAIL
        return PolicyResult(
            policy_id=self.policy_id,
            policy_name=self.policy_name,
            category=self.category,
            status=status,
            severity=self.severity,
            evidence={"incident_severity": target.get("severity"), "open_hours": target.get("open_hours", 0)},
            recommendation="No action required." if satisfied else "Escalate critical unmitigated incident to tier 2 support.",
        )
