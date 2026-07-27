export interface MetricSnapshot {
  id: string;
  metric_name: string;
  metric_type: "latency" | "throughput" | "request_count" | "error_count" | "worker_utilization" | "queue_depth" | "duration";
  value: number;
  unit: string;
  labels?: Record<string, any>;
  created_at: string;
}

export interface Span {
  id: string;
  span_id: string;
  trace_id_str: string;
  parent_span_id?: string;
  name: string;
  service_name: string;
  status: "ok" | "error" | "unset";
  duration_ms: number;
  attributes?: Record<string, any>;
  start_time: string;
  end_time: string;
}

export interface Trace {
  id: string;
  trace_id: string;
  name: string;
  service_name: string;
  duration_ms: number;
  status: "ok" | "error" | "unset";
  start_time: string;
  end_time: string;
  spans: Span[];
}

export interface SubsystemHealth {
  status: string;
  subsystems: Record<string, "healthy" | "degraded" | "unhealthy">;
  timestamp: string;
}
