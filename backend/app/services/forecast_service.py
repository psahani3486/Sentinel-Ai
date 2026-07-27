"""
Sentinel AI — Forecast Service

Service layer managing telemetry extraction, forecasting strategy execution,
confidence interval generation, and report persistence.
"""

import logging
import uuid
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.forecasting.base_strategy import ForecastContext
from app.forecasting.engine import ForecastEngine
from app.forecasting.reporter import ForecastReporter
from app.models.enums import ForecastType
from app.models.forecasting import ForecastResult, ForecastRun
from app.repositories.forecasting_repository import (
    ForecastResultRepository,
    ForecastRunRepository,
)

logger = logging.getLogger(__name__)


class ForecastService:
    """Coordinates predictive forecasting strategy execution and persistence."""

    def __init__(
        self,
        db_session: AsyncSession,
        run_repo: ForecastRunRepository | None = None,
        result_repo: ForecastResultRepository | None = None,
        engine: ForecastEngine | None = None,
        reporter: ForecastReporter | None = None,
    ) -> None:
        self._session = db_session
        self._run_repo = run_repo or ForecastRunRepository(db_session)
        self._result_repo = result_repo or ForecastResultRepository(db_session)
        self._engine = engine or ForecastEngine()
        self._reporter = reporter or ForecastReporter()

    def _sanitize_dict(self, d: dict[str, Any]) -> dict[str, Any]:
        """Convert non-JSON serializable objects into strings for JSON storage."""
        sanitized = {}
        for k, v in d.items():
            if isinstance(v, uuid.UUID):
                sanitized[k] = str(v)
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_dict(v)
            else:
                sanitized[k] = v
        return sanitized

    async def run_forecast(
        self,
        forecast_type: ForecastType,
        dataset_id: uuid.UUID | None = None,
        horizon_days: int = 7,
        historical_series: list[float] | None = None,
    ) -> ForecastRun:
        """Gather context, execute forecast engine, and persist forecast run and results."""
        context = ForecastContext(
            forecast_type=forecast_type,
            dataset_id=dataset_id,
            historical_series=historical_series or [],
            horizon_days=horizon_days,
        )

        res = self._engine.run_forecast(context)

        run_entity = ForecastRun(
            dataset_id=dataset_id,
            forecast_type=forecast_type,
            algorithm_name=res.algorithm_name,
            forecast_horizon_days=horizon_days,
            overall_risk_level=res.overall_risk_level,
            summary=res.summary,
            execution_time_ms=res.execution_time_ms,
            status="completed",
        )
        run_entity = await self._run_repo.create(run_entity)

        for dp in res.datapoints:
            result_entity = ForecastResult(
                forecast_run_id=run_entity.id,
                target_metric=dp.target_metric,
                predicted_value=dp.predicted_value,
                confidence_interval_lower=dp.confidence_interval_lower,
                confidence_interval_upper=dp.confidence_interval_upper,
                trend_direction=dp.trend_direction,
                risk_level=dp.risk_level,
                explanation=dp.explanation,
                preventive_actions={"actions": dp.preventive_actions},
            )
            await self._result_repo.create(result_entity)

        logger.info("Executed Forecast Run '%s' -> Type: %s, Risk: %s",
                    run_entity.id, forecast_type.value, res.overall_risk_level.value)

        return await self._run_repo.get_by_id_with_results(run_entity.id) or run_entity

    async def get_history(self, skip: int = 0, limit: int = 50) -> Sequence[ForecastRun]:
        """Fetch paginated forecast history."""
        return await self._run_repo.get_history(skip=skip, limit=limit)

    async def get_by_id(self, run_id: uuid.UUID) -> ForecastRun | None:
        """Fetch forecast run by ID with results."""
        return await self._run_repo.get_by_id_with_results(run_id)
