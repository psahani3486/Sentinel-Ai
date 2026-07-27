"""
Sentinel AI — Telemetry Service

Service layer managing metric collection, APM trace persistence, and subsystem health evaluations.
"""

import datetime
import logging
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.telemetry import MetricSnapshot, Span, Trace
from app.repositories.telemetry_repository import (
    MetricSnapshotRepository,
    SpanRepository,
    TraceRepository,
)
from app.telemetry.engine import TelemetryEngine
from app.telemetry.reporter import TelemetryReporter

logger = logging.getLogger(__name__)


class TelemetryService:
    """Coordinates metric collection, APM tracing, and health evaluations."""

    def __init__(
        self,
        db_session: AsyncSession,
        metric_repo: MetricSnapshotRepository | None = None,
        trace_repo: TraceRepository | None = None,
        span_repo: SpanRepository | None = None,
        engine: TelemetryEngine | None = None,
        reporter: TelemetryReporter | None = None,
    ) -> None:
        self._session = db_session
        self._metric_repo = metric_repo or MetricSnapshotRepository(db_session)
        self._trace_repo = trace_repo or TraceRepository(db_session)
        self._span_repo = span_repo or SpanRepository(db_session)
        self._engine = engine or TelemetryEngine()
        self._reporter = reporter or TelemetryReporter()

    async def seed_initial_telemetry(self) -> list[MetricSnapshot]:
        """Collect metrics, generate APM trace, and seed initial database entities."""
        metrics_data = self._engine.collect_metrics()
        created_metrics = []

        for m in metrics_data:
            m_entity = MetricSnapshot(
                metric_name=m.metric_name,
                metric_type=m.metric_type,
                value=m.value,
                unit=m.unit,
                labels=m.labels,
            )
            m_entity = await self._metric_repo.create(m_entity)
            created_metrics.append(m_entity)

        # Generate sample APM Trace
        tctx = self._engine.generate_trace()
        now = datetime.datetime.now(datetime.timezone.utc)

        t_entity = Trace(
            trace_id=tctx.trace_id,
            name=tctx.name,
            service_name=tctx.service_name,
            duration_ms=tctx.duration_ms,
            status=tctx.status,
            start_time=now,
            end_time=now + datetime.timedelta(milliseconds=tctx.duration_ms),
        )
        t_entity = await self._trace_repo.create(t_entity)

        for sdata in tctx.spans:
            s_entity = Span(
                trace_pk=t_entity.id,
                span_id=sdata.span_id,
                trace_id_str=tctx.trace_id,
                parent_span_id=sdata.parent_span_id,
                name=sdata.name,
                service_name=sdata.service_name,
                status=sdata.status,
                duration_ms=sdata.duration_ms,
                attributes=sdata.attributes,
                start_time=sdata.start_time,
                end_time=sdata.end_time,
            )
            await self._span_repo.create(s_entity)

        logger.info("Seeded initial platform telemetry metrics and APM trace '%s'", tctx.trace_id)
        return created_metrics

    async def get_metrics(self) -> Sequence[MetricSnapshot]:
        """Fetch latest metric snapshots."""
        metrics = await self._metric_repo.get_latest_metrics()
        if not metrics:
            return await self.seed_initial_telemetry()
        return metrics

    async def get_health(self) -> dict[str, Any]:
        """Evaluate platform subsystem health statuses."""
        health_map = self._engine.evaluate_subsystem_health()
        return {
            "status": "healthy",
            "subsystems": {k: v.value for k, v in health_map.items()},
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

    async def get_traces(self) -> Sequence[Trace]:
        """Fetch recent APM trace contexts."""
        traces = await self._trace_repo.get_recent_traces()
        if not traces:
            await self.seed_initial_telemetry()
            return await self._trace_repo.get_recent_traces()
        return traces

    async def get_trace_detail(self, trace_id_str: str) -> Trace | None:
        """Fetch detailed trace by trace_id string with spans."""
        return await self._trace_repo.get_by_trace_id_with_spans(trace_id_str)
