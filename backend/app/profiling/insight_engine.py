"""
Sentinel AI — Dataset Insight Engine

Rule-based heuristic engine analyzing dataset column profiles to detect anomaly patterns:
- High missing value columns (>20% null)
- Constant columns (single unique value)
- High cardinality columns (>80% unique non-id)
- Low cardinality columns (<5% unique)
- Highly skewed columns (|skewness| > 1.0)
- Candidate primary keys (100% unique, 0% null)
- Identifier candidates, Timestamp candidates, Target column candidates
"""

from typing import Any


class InsightEngine:
    """Engine that generates domain and statistical insights from dataset column profiles."""

    TARGET_PATTERNS = [
        "target",
        "label",
        "failure",
        "rul",
        "status",
        "fault",
        "pass_fail",
        "class",
    ]
    TIMESTAMP_PATTERNS = ["time", "timestamp", "date", "cycle", "datetime", "t_stamp"]
    IDENTIFIER_PATTERNS = ["id", "udi", "unit", "machine", "product", "serial", "device"]

    @classmethod
    def generate_insights(
        self, column_profiles: list[dict[str, Any]], total_rows: int
    ) -> dict[str, Any]:
        """
        Generate automated dataset insights from column profiles.

        Args:
            column_profiles: List of detailed column profile dictionaries.
            total_rows: Total dataset row count.

        Returns:
            Dict containing lists of flagged column names per category and actionable warnings.
        """
        high_missing: list[dict[str, Any]] = []
        constant_cols: list[str] = []
        high_cardinality: list[dict[str, Any]] = []
        low_cardinality: list[dict[str, Any]] = []
        highly_skewed: list[dict[str, Any]] = []
        candidate_primary_keys: list[str] = []
        possible_identifiers: list[str] = []
        timestamp_candidates: list[str] = []
        possible_targets: list[str] = []

        actionable_warnings: list[str] = []

        for col in column_profiles:
            col_name = col["column_name"]
            col_name_lower = col_name.lower()
            completeness = col["completeness"]
            uniqueness = col["uniqueness"]

            null_pct = completeness["null_percentage"]
            null_count = completeness["null_count"]
            unique_count = uniqueness["unique_count"]
            unique_pct = uniqueness["unique_percentage"]

            # 1. High Missing Values (>20%)
            if null_pct > 20.0:
                high_missing.append({"column_name": col_name, "null_percentage": null_pct})
                actionable_warnings.append(
                    f"Column '{col_name}' has high missing values ({null_pct}% null)."
                )

            # 2. Constant Columns (Single unique value)
            if unique_count == 1:
                constant_cols.append(col_name)
                actionable_warnings.append(
                    f"Column '{col_name}' is constant (has only 1 distinct value)."
                )

            # 3. Candidate Primary Keys (0% null, 100% unique)
            if null_count == 0 and unique_count == total_rows and total_rows > 0:
                candidate_primary_keys.append(col_name)

            # 4. High Cardinality (>80% unique, non-primary key)
            elif unique_pct > 80.0 and total_rows > 10:
                high_cardinality.append({"column_name": col_name, "unique_percentage": unique_pct})

            # 5. Low Cardinality (<5% unique, >1 unique)
            if 1 < unique_count and unique_pct < 5.0 and total_rows > 20:
                low_cardinality.append({"column_name": col_name, "unique_count": unique_count})

            # 6. Highly Skewed Numeric Columns (|skewness| > 1.0)
            if col.get("type_category") == "numeric":
                stats = col.get("statistics", {})
                skewness = stats.get("skewness", 0.0)
                if skewness and abs(skewness) > 1.0:
                    highly_skewed.append({"column_name": col_name, "skewness": skewness})

            # 7. Domain Candidate Pattern Matching
            if any(p in col_name_lower for p in self.TIMESTAMP_PATTERNS):
                timestamp_candidates.append(col_name)

            if any(p in col_name_lower for p in self.TARGET_PATTERNS):
                possible_targets.append(col_name)

            if any(p in col_name_lower for p in self.IDENTIFIER_PATTERNS):
                possible_identifiers.append(col_name)

        return {
            "high_missing_value_columns": high_missing,
            "constant_columns": constant_cols,
            "high_cardinality_columns": high_cardinality,
            "low_cardinality_columns": low_cardinality,
            "highly_skewed_columns": highly_skewed,
            "candidate_primary_keys": candidate_primary_keys,
            "possible_identifier_columns": possible_identifiers,
            "timestamp_candidates": timestamp_candidates,
            "possible_target_columns": possible_targets,
            "actionable_warnings": actionable_warnings,
        }
