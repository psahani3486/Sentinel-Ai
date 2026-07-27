"""
Sentinel AI — Job Executor

Executes background jobs asynchronously based on JobType (DATASET_UPLOAD, DATA_PROFILING,
DATA_VALIDATION). Designed via interface abstractions so Redis / Celery workers can reuse
the exact same executor logic.
"""

import logging
import os
import time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dataset import DatasetColumn, DatasetSchema
from app.models.enums import ConnectorType, JobType
from app.models.job import Job
from app.repositories.dataset_repository import (
    DatasetColumnRepository,
    DatasetProfileRepository,
    DatasetRepository,
    DatasetSchemaRepository,
    DatasetVersionRepository,
)
from app.repositories.validation_repository import (
    ValidationResultRepository,
    ValidationRunRepository,
)
from app.services.connector_service import ConnectorService
from app.services.profiling_service import ProfilingService
from app.services.validation_service import ValidationService

logger = logging.getLogger(__name__)


class JobExecutor:
    """Dispatches and executes background jobs with fine-grained progress updates."""

    def __init__(
        self,
        connector_service: ConnectorService | None = None,
        profiling_service: ProfilingService | None = None,
        validation_service: ValidationService | None = None,
    ) -> None:
        self._connector_svc = connector_service or ConnectorService()
        self._profiling_svc = profiling_service or ProfilingService()
        self._validation_svc = validation_service or ValidationService()

    async def execute(self, job: Job, db: AsyncSession) -> dict[str, Any]:
        """
        Execute a background job payload based on its JobType.

        Args:
            job: Target Job ORM entity.
            db: Database session.

        Returns:
            Dict containing execution results and metadata.
        """
        start_time = time.time()
        metadata = job.job_metadata or {}

        if job.job_type == JobType.DATASET_UPLOAD:
            result = await self._execute_upload(job, db, metadata)
        elif job.job_type == JobType.DATA_PROFILING:
            result = await self._execute_profiling(job, db, metadata)
        elif job.job_type == JobType.DATA_VALIDATION:
            result = await self._execute_validation(job, db, metadata)
        else:
            raise ValueError(f"Unsupported job type: {job.job_type}")

        exec_time = round((time.time() - start_time) * 1000, 2)
        result["execution_time_ms"] = exec_time
        return result

    async def _execute_upload(
        self, job: Job, db: AsyncSession, metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute DATASET_UPLOAD background job."""
        file_path = metadata.get("file_path")
        if not file_path or not os.path.exists(file_path):
            raise FileNotFoundError(f"Target upload file not found: {file_path}")

        connector_type = ConnectorType(metadata.get("connector_type", ConnectorType.CSV))
        config = {"file_path": file_path}

        version_repo = DatasetVersionRepository(db)
        schema_repo = DatasetSchemaRepository(db)
        col_repo = DatasetColumnRepository(db)
        profile_repo = DatasetProfileRepository(db)
        profiling_svc = ProfilingService(profile_repository=profile_repo)

        # 1. Schema Discovery
        schema_list = self._connector_svc.fetch_schema(connector_type, config)

        if job.dataset_version_id:
            version = await version_repo.get_by_id(job.dataset_version_id)
        else:
            version = None

        if version:
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

            # 2. Automated Profile
            profile = await profiling_svc.profile_and_persist(version.id, connector_type, config)
            await version_repo.update(
                version, {"row_count": profile.total_rows, "column_count": profile.total_columns}
            )
            return {
                "dataset_version_id": str(version.id),
                "total_rows": profile.total_rows,
                "total_columns": profile.total_columns,
            }

        return {"schema_columns_count": len(schema_list)}

    async def _execute_profiling(
        self, job: Job, db: AsyncSession, metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute DATA_PROFILING background job."""
        version_id = job.dataset_version_id or metadata.get("dataset_version_id")
        if not version_id:
            raise ValueError("DATA_PROFILING job requires dataset_version_id")

        version_repo = DatasetVersionRepository(db)
        dataset_repo = DatasetRepository(db)
        profile_repo = DatasetProfileRepository(db)
        profiling_svc = ProfilingService(profile_repository=profile_repo)

        version = await version_repo.get_by_id(version_id)
        if not version:
            raise ValueError(f"DatasetVersion '{version_id}' not found")

        dataset = await dataset_repo.get_by_id(version.dataset_id)
        conn_type = dataset.connector_type if dataset else ConnectorType.CSV
        config = {"file_path": version.storage_path}

        profile = await profiling_svc.profile_and_persist(version.id, conn_type, config)
        return {
            "dataset_version_id": str(version.id),
            "total_rows": profile.total_rows,
            "total_columns": profile.total_columns,
            "profile_id": str(profile.id),
        }

    async def _execute_validation(
        self, job: Job, db: AsyncSession, metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute DATA_VALIDATION background job."""
        version_id = job.dataset_version_id or metadata.get("dataset_version_id")
        if not version_id:
            raise ValueError("DATA_VALIDATION job requires dataset_version_id")

        version_repo = DatasetVersionRepository(db)
        dataset_repo = DatasetRepository(db)
        run_repo = ValidationRunRepository(db)
        res_repo = ValidationResultRepository(db)
        val_svc = ValidationService(
            run_repository=run_repo,
            result_repository=res_repo,
            version_repository=version_repo,
        )

        version = await version_repo.get_by_id(version_id)
        if not version:
            raise ValueError(f"DatasetVersion '{version_id}' not found")

        dataset = await dataset_repo.get_by_id(version.dataset_id)
        conn_type = dataset.connector_type if dataset else ConnectorType.CSV
        config = {"file_path": version.storage_path}
        rules = metadata.get("rules")

        db_run = await val_svc.run_and_persist(version.id, conn_type, config, rules=rules)
        return {
            "validation_run_id": str(db_run.id),
            "status": db_run.status.value if hasattr(db_run.status, "value") else str(db_run.status),
            "overall_score": db_run.overall_score,
        }
