"""
Sentinel AI — Phase 3C WebSocket & EventBus Test Suite

Tests EventBus publishing/subscription, JobService event emission,
ConnectionManager multi-client broadcasting, stale connection cleanup,
and FastAPI WebSocket streaming endpoints.
"""

import uuid
import pytest
from unittest.mock import AsyncMock

from app.api.v1.endpoints.websocket import ConnectionManager
from app.events.event_bus import InMemoryEventBus
from app.events.events import (
    JobCreatedEvent,
    JobEvent,
    JobProgressUpdatedEvent,
)
from app.models.enums import JobStatus, JobType
from app.repositories.job_repository import JobRepository
from app.services.job_service import JobService


@pytest.mark.asyncio
async def test_in_memory_event_bus_pub_sub():
    """Test InMemoryEventBus subscription, wildcard '*', and unsubscription handling."""
    bus = InMemoryEventBus()

    received_specific: list[JobEvent] = []
    received_wildcard: list[JobEvent] = []

    async def specific_handler(event: JobEvent):
        received_specific.append(event)

    async def wildcard_handler(event: JobEvent):
        received_wildcard.append(event)

    bus.subscribe("job_created", specific_handler)
    bus.subscribe("*", wildcard_handler)

    test_event = JobCreatedEvent(
        job_id=uuid.uuid4(),
        job_type=JobType.DATA_PROFILING,
        status=JobStatus.PENDING,
        progress_percentage=0.0,
    )

    await bus.publish(test_event)

    assert len(received_specific) == 1
    assert len(received_wildcard) == 1
    assert received_specific[0].job_id == test_event.job_id

    # Unsubscribe test
    bus.unsubscribe("job_created", specific_handler)
    await bus.publish(test_event)

    assert len(received_specific) == 1
    assert len(received_wildcard) == 2


@pytest.mark.asyncio
async def test_job_service_publishes_events(db_session, test_user):
    """Test that JobService state transitions automatically emit events to EventBus."""
    bus = InMemoryEventBus()
    job_repo = JobRepository(db_session)
    svc = JobService(job_repository=job_repo, event_bus=bus)

    emitted_events: list[JobEvent] = []

    async def capture_event(evt: JobEvent):
        emitted_events.append(evt)

    bus.subscribe("*", capture_event)

    # 1. Create Job
    job = await svc.create_job(job_type=JobType.DATA_VALIDATION, created_by_id=test_user.id)
    assert len(emitted_events) == 1
    assert emitted_events[0].event_type == "job_created"

    # 2. Queue Job
    await svc.queue_job(job.id)
    assert len(emitted_events) == 2
    assert emitted_events[1].event_type == "job_queued"

    # 3. Start Job
    await svc.start_job(job.id)
    assert len(emitted_events) == 3
    assert emitted_events[2].event_type == "job_started"

    # 4. Progress Update
    await svc.update_progress(job.id, 50.0, "Validating rules...")
    assert len(emitted_events) == 4
    assert emitted_events[3].event_type == "job_progress_updated"
    assert emitted_events[3].progress_percentage == 50.0

    # 5. Complete Job
    await svc.complete_job(job.id)
    assert len(emitted_events) == 5
    assert emitted_events[4].event_type == "job_completed"


@pytest.mark.asyncio
async def test_connection_manager_broadcasting_and_stale_cleanup():
    """Test ConnectionManager connecting, sending, stale socket cleanup, and disconnecting."""
    mgr = ConnectionManager()

    mock_global_ws = AsyncMock()
    mock_job_ws = AsyncMock()
    mock_stale_ws = AsyncMock()
    mock_stale_ws.send_text.side_effect = RuntimeError("Broken pipe")

    job_id_str = str(uuid.uuid4())

    await mgr.connect_global(mock_global_ws)
    await mgr.connect_job(mock_job_ws, job_id_str)
    await mgr.connect_job(mock_stale_ws, job_id_str)

    event = JobProgressUpdatedEvent(
        job_id=uuid.UUID(job_id_str),
        job_type=JobType.DATA_PROFILING,
        status=JobStatus.RUNNING,
        progress_percentage=60.0,
        latest_message="Profiling columns...",
    )

    await mgr.on_job_event(event)

    mock_global_ws.send_text.assert_called_once()
    mock_job_ws.send_text.assert_called_once()

    # Stale socket should have been disconnected automatically
    assert mock_stale_ws not in mgr._job_subscribers.get(job_id_str, set())

    mgr.disconnect_global(mock_global_ws)
    mgr.disconnect_job(mock_job_ws, job_id_str)


@pytest.mark.asyncio
async def test_websocket_endpoints():
    """Test FastAPI WebSocket endpoints /api/v1/ws/jobs and /api/v1/ws/jobs/{id}."""
    from fastapi.testclient import TestClient
    from app.main import app

    test_client = TestClient(app)
    job_id_str = str(uuid.uuid4())

    with test_client.websocket_connect("/api/v1/ws/jobs") as ws_global:
        ws_global.send_text("ping")
        resp = ws_global.receive_text()
        assert resp == "pong"

    with test_client.websocket_connect(f"/api/v1/ws/jobs/{job_id_str}") as ws_job:
        ws_job.send_text("ping")
        resp = ws_job.receive_text()
        assert resp == "pong"
