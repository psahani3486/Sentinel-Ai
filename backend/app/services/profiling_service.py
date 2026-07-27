"""
Sentinel AI — Profiling Service

High-level business service connecting ConnectorService, DatasetProfiler,
and DatasetProfileRepository to profile datasets, persist profile records,
and perform version-to-version statistical comparisons.
"""

import logging
import uuid
from typing import Any

from app.models.dataset import DatasetProfile
from app.models.enums import ConnectorType
from app.profiling.dataset_profiler import DatasetProfiler
from app.repositories.dataset_repository import DatasetProfileRepository
from app.services.connector_service import ConnectorService

logger = logging.getLogger(__name__)


class ProfilingService:
    """Service layer managing data profiling, persistence, and version comparisons."""

    def __init__(
        self,
        connector_service: ConnectorService | None = None,
        profile_repository: DatasetProfileRepository | None = None,
        dataset_profiler: DatasetProfiler | None = None,
    ) -> None:
        self._connector_service = connector_service or ConnectorService()
        self._profile_repo = profile_repository
        self._dataset_profiler = dataset_profiler or DatasetProfiler()

    def generate_profile(
        self, connector_type: ConnectorType | str, config: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Read dataset via Connector and generate complete statistical profile.

        Args:
            connector_type: Connector type enum or string.
            config: Connector configuration dictionary.

        Returns:
            Dict containing full dataset profile data.
        """
        connector = self._connector_service.create_connector(connector_type, config)
        try:
            connector.connect()
            metadata = connector.get_metadata()
            file_size = metadata.get("file_size_bytes", 0)

            df = connector.read()
            if hasattr(df, "__next__"):
                profile = self._dataset_profiler.profile_stream(df, file_size_bytes=file_size)
            else:
                profile = self._dataset_profiler.profile_dataframe(df, file_size_bytes=file_size)

            logger.info(
                "Generated profile for %s (rows: %s, cols: %s)",
                connector.__class__.__name__,
                profile["dataset_metrics"]["row_count"],
                profile["dataset_metrics"]["column_count"],
            )
            return profile
        finally:
            connector.disconnect()

    async def profile_and_persist(
        self,
        dataset_version_id: uuid.UUID,
        connector_type: ConnectorType | str,
        config: dict[str, Any],
    ) -> DatasetProfile:
        """
        Generate dataset profile and persist record into the database.

        Raises:
            ValueError: If profile_repository was not injected.
        """
        if not self._profile_repo:
            raise ValueError("ProfilingService requires a DatasetProfileRepository for persistence")

        profile_dict = self.generate_profile(connector_type, config)
        metrics = profile_dict["dataset_metrics"]

        # Check if profile already exists for this version
        existing_profile = await self._profile_repo.get_by_version_id(dataset_version_id)
        if existing_profile:
            updated = await self._profile_repo.update(
                existing_profile,
                {
                    "total_rows": metrics["row_count"],
                    "total_columns": metrics["column_count"],
                    "memory_bytes": metrics["memory_bytes"],
                    "profile_data": profile_dict,
                },
            )
            return updated

        new_profile = DatasetProfile(
            dataset_version_id=dataset_version_id,
            total_rows=metrics["row_count"],
            total_columns=metrics["column_count"],
            memory_bytes=metrics["memory_bytes"],
            profile_data=profile_dict,
        )
        return await self._profile_repo.create(new_profile)

    def compare_profiles(
        self, profile_v1: dict[str, Any], profile_v2: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Compare two statistical dataset profiles across dataset versions.

        Returns:
            Dict highlighting row_count_diff, memory_diff, added_columns, removed_columns,
            and column statistic diffs.
        """
        m1 = profile_v1.get("dataset_metrics", {})
        m2 = profile_v2.get("dataset_metrics", {})

        cols_v1 = {c["column_name"]: c for c in profile_v1.get("column_profiles", [])}
        cols_v2 = {c["column_name"]: c for c in profile_v2.get("column_profiles", [])}

        added_cols = list(set(cols_v2.keys()) - set(cols_v1.keys()))
        removed_cols = list(set(cols_v1.keys()) - set(cols_v2.keys()))
        common_cols = list(set(cols_v1.keys()) & set(cols_v2.keys()))

        column_diffs: dict[str, Any] = {}
        for col_name in common_cols:
            c1 = cols_v1[col_name]
            c2 = cols_v2[col_name]

            null_pct_diff = round(
                c2["completeness"]["null_percentage"] - c1["completeness"]["null_percentage"], 2
            )
            unique_pct_diff = round(
                c2["uniqueness"]["unique_percentage"] - c1["uniqueness"]["unique_percentage"], 2
            )

            column_diffs[col_name] = {
                "null_percentage_diff": null_pct_diff,
                "unique_percentage_diff": unique_pct_diff,
            }

        return {
            "row_count_diff": m2.get("row_count", 0) - m1.get("row_count", 0),
            "column_count_diff": m2.get("column_count", 0) - m1.get("column_count", 0),
            "memory_bytes_diff": m2.get("memory_bytes", 0) - m1.get("memory_bytes", 0),
            "added_columns": added_cols,
            "removed_columns": removed_cols,
            "column_diffs": column_diffs,
        }
