"""
Sentinel AI — Catalog Reporter

Formats lineage DAGs and governance compliance scores for UI display.
"""

from typing import Any


class CatalogReporter:
    """Formats data catalog telemetry summary."""

    def build_dashboard_summary(self, assets: list[Any], policies: list[Any]) -> dict[str, Any]:
        """Build catalog ecosystem summary."""
        compliant_cnt = sum(1 for p in policies if str(getattr(p, "compliance_status", "COMPLIANT")).upper() == "COMPLIANT")
        total_policies = len(policies)
        total_assets = len(assets)

        return {
            "total_catalog_assets": total_assets,
            "total_governance_policies": total_policies,
            "compliant_policies_count": compliant_cnt,
            "compliance_rate_percent": (compliant_cnt / total_policies * 100.0) if total_policies > 0 else 100.0,
        }
