"""
Sentinel AI — WebSocket Endpoints & Real-Time Progress Streaming

Provides real-time WebSocket endpoints for streaming background job progress events.
Subscribes to EventBus for non-blocking Event -> WebSocket broadcasting.
"""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.events.event_bus import get_event_bus
from app.events.events import JobEvent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSockets"])


class ConnectionManager:
    """
    Manages active WebSocket client connections, subscription channels,
    stale socket cleanup, and thread-safe JSON event broadcasting.
    """

    def __init__(self) -> None:
        # Subscribers for specific job IDs: job_id_str -> set of WebSockets
        self._job_subscribers: dict[str, set[WebSocket]] = {}
        # Global subscribers listening to all jobs
        self._global_subscribers: set[WebSocket] = set()
        self._subscribed_to_bus = False

    def setup_event_bus_subscription(self) -> None:
        """Subscribe to global EventBus wildcard events."""
        if not self._subscribed_to_bus:
            event_bus = get_event_bus()
            event_bus.subscribe("*", self.on_job_event)
            self._subscribed_to_bus = True
            logger.info("ConnectionManager subscribed to global EventBus '*' wildcard channel.")

    async def connect_global(self, websocket: WebSocket) -> None:
        """Connect a client listening to global job progress telemetry."""
        await websocket.accept()
        self._global_subscribers.add(websocket)
        self.setup_event_bus_subscription()
        logger.info("Global WebSocket client connected. Active global sockets: %d", len(self._global_subscribers))

    def disconnect_global(self, websocket: WebSocket) -> None:
        """Disconnect a global telemetry client."""
        self._global_subscribers.discard(websocket)
        logger.info("Global WebSocket client disconnected. Remaining: %d", len(self._global_subscribers))

    async def connect_job(self, websocket: WebSocket, job_id: str) -> None:
        """Connect a client listening to a specific job ID telemetry channel."""
        await websocket.accept()
        if job_id not in self._job_subscribers:
            self._job_subscribers[job_id] = set()
        self._job_subscribers[job_id].add(websocket)
        self.setup_event_bus_subscription()
        logger.info("Job WebSocket client connected to job '%s'. Total job sockets: %d", job_id, len(self._job_subscribers[job_id]))

    def disconnect_job(self, websocket: WebSocket, job_id: str) -> None:
        """Disconnect a specific job ID telemetry client."""
        if job_id in self._job_subscribers:
            self._job_subscribers[job_id].discard(websocket)
            if not self._job_subscribers[job_id]:
                del self._job_subscribers[job_id]
        logger.info("Job WebSocket client disconnected from job '%s'.", job_id)

    async def on_job_event(self, event: JobEvent) -> None:
        """Callback handler invoked by EventBus when a job event is published."""
        payload_str = json.dumps(
            {
                "job_id": str(event.job_id),
                "job_type": event.job_type.value if hasattr(event.job_type, "value") else str(event.job_type),
                "status": event.status.value if hasattr(event.status, "value") else str(event.status),
                "progress_percentage": event.progress_percentage,
                "latest_message": event.latest_message,
                "execution_time_ms": event.execution_time_ms,
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
                "metadata": event.metadata,
            }
        )

        stale_sockets: set[WebSocket] = set()
        job_id_str = str(event.job_id)

        # 1. Broadcast to job-specific subscribers
        job_sockets = list(self._job_subscribers.get(job_id_str, set()))
        for ws in job_sockets:
            try:
                await ws.send_text(payload_str)
            except Exception:
                stale_sockets.add(ws)

        for ws in stale_sockets:
            self.disconnect_job(ws, job_id_str)

        # 2. Broadcast to global subscribers
        stale_global: set[WebSocket] = set()
        global_sockets = list(self._global_subscribers)
        for ws in global_sockets:
            try:
                await ws.send_text(payload_str)
            except Exception:
                stale_global.add(ws)

        for ws in stale_global:
            self.disconnect_global(ws)


ws_manager = ConnectionManager()


@router.websocket("/jobs")
async def websocket_global_jobs(websocket: WebSocket) -> None:
    """WebSocket endpoint streaming progress updates across all background jobs."""
    await ws_manager.connect_global(websocket)
    try:
        while True:
            # Keep socket alive and receive client ping messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect_global(websocket)
    except Exception as e:
        logger.warning("Global WebSocket error: %s", e)
        ws_manager.disconnect_global(websocket)


@router.websocket("/jobs/{job_id}")
async def websocket_specific_job(websocket: WebSocket, job_id: str) -> None:
    """WebSocket endpoint streaming progress updates for a specific job ID."""
    await ws_manager.connect_job(websocket, job_id)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect_job(websocket, job_id)
    except Exception as e:
        logger.warning("Job WebSocket error for job '%s': %s", job_id, e)
        ws_manager.disconnect_job(websocket, job_id)
