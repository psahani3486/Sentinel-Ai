"use client";

import { useEffect, useState, useRef } from "react";

export interface JobProgressEvent {
  job_id: string;
  job_type: string;
  status: string;
  progress_percentage: number;
  latest_message?: string;
  execution_time_ms: number;
  event_type: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export function useJobWebSocket(jobId?: string) {
  const [lastEvent, setLastEvent] = useState<JobProgressEvent | null>(null);
  const [activeJobs, setActiveJobs] = useState<Record<string, JobProgressEvent>>({});
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let socket: WebSocket | null = null;
    let isComponentMounted = true;
    let pingInterval: NodeJS.Timeout | null = null;

    function getWsUrl(): string {
      if (process.env.NEXT_PUBLIC_WS_URL) {
        const base = process.env.NEXT_PUBLIC_WS_URL.replace(/\/$/, "");
        return jobId ? `${base}/jobs/${jobId}` : `${base}/jobs`;
      }
      if (typeof window !== "undefined") {
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const host = window.location.hostname === "localhost" ? "127.0.0.1" : window.location.hostname;
        return jobId
          ? `${protocol}//${host}:8000/api/v1/ws/jobs/${jobId}`
          : `${protocol}//${host}:8000/api/v1/ws/jobs`;
      }
      return jobId
        ? `ws://127.0.0.1:8000/api/v1/ws/jobs/${jobId}`
        : `ws://127.0.0.1:8000/api/v1/ws/jobs`;
    }

    function connect() {
      try {
        const wsUrl = getWsUrl();
        socket = new WebSocket(wsUrl);
        wsRef.current = socket;

        socket.onopen = () => {
          if (isComponentMounted) {
            setIsConnected(true);
            // Send periodic ping to keep socket alive
            pingInterval = setInterval(() => {
              if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send("ping");
              }
            }, 15000);
          }
        };

        socket.onmessage = (evt) => {
          if (!isComponentMounted) return;
          try {
            if (evt.data === "pong") return;
            const data: JobProgressEvent = JSON.parse(evt.data);
            setLastEvent(data);
            setActiveJobs((prev) => ({ ...prev, [data.job_id]: data }));
          } catch (e) {
            console.error("Failed to parse WebSocket job message:", e);
          }
        };

        socket.onclose = () => {
          if (pingInterval) clearInterval(pingInterval);
          if (isComponentMounted) {
            setIsConnected(false);
            // Reconnect automatically after 3s
            setTimeout(() => {
              if (isComponentMounted) connect();
            }, 3000);
          }
        };

        socket.onerror = () => {
          if (isComponentMounted) {
            setIsConnected(false);
          }
        };
      } catch (err) {
        console.warn("WebSocket connection initialization failed:", err);
      }
    }

    connect();

    return () => {
      isComponentMounted = false;
      if (pingInterval) clearInterval(pingInterval);
      if (socket) {
        socket.close();
      }
    };
  }, [jobId]);

  return { lastEvent, activeJobs, isConnected };
}
