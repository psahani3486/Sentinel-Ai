"""
Sentinel AI — Telemetry Repositories

Repository layer for persisting, querying, and sorting MetricSnapshot, Trace, and Span entities.
"""

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.telemetry import MetricSnapshot, Span, Trace
from app.repositories.base import BaseRepository


class MetricSnapshotRepository(BaseRepository[MetricSnapshot]):
    """Repository for managing MetricSnapshot entities."""

    def __init__(self, session) -> None:
        super().__init__(MetricSnapshot, session)

    async def get_latest_metrics(self, limit: int = 50) -> Sequence[MetricSnapshot]:
        """Fetch latest metric snapshots ordered by created_at desc."""
        stmt = select(MetricSnapshot).order_by(MetricSnapshot.created_at.desc()).limit(limit)
        res = await self._session.execute(stmt)
        return res.scalars().all()


class TraceRepository(BaseRepository[Trace]):
    """Repository for managing Trace entities."""

    def __init__(self, session) -> None:
        super().__init__(Trace, session)

    async def get_by_trace_id_with_spans(self, trace_id_str: str) -> Trace | None:
        """Fetch Trace by trace_id string including spans."""
        stmt = (
            select(Trace)
            .where(Trace.trace_id == trace_id_str)
            .options(selectinload(Trace.spans))
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_recent_traces(self, limit: int = 50) -> Sequence[Trace]:
        """Fetch recent APM traces ordered by start_time desc."""
        stmt = (
            select(Trace)
            .options(selectinload(Trace.spans))
            .order_by(Trace.start_time.desc())
            .limit(limit)
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()


class SpanRepository(BaseRepository[Span]):
    """Repository for managing Span entities."""

    def __init__(self, session) -> None:
        super().__init__(Span, session)

    async def get_spans_for_trace(self, trace_id_str: str) -> Sequence[Span]:
        """Fetch spans for a trace ordered by start_time asc."""
        stmt = (
            select(Span)
            .where(Span.trace_id_str == trace_id_str)
            .order_by(Span.start_time.asc())
        )
        res = await self._session.execute(stmt)
        return res.scalars().all()
