export interface IncidentEvent {
  id: string;
  timestamp: string;
  event_type: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  description: string;
  evidence_link?: string;
  payload?: Record<string, any>;
  created_at: string;
}

export interface Incident {
  id: string;
  dataset_id?: string;
  rca_id?: string;
  recommendation_id?: string;
  forecast_id?: string;
  title: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  status: "open" | "investigating" | "mitigated" | "resolved" | "closed";
  summary: string;
  root_cause_summary?: string;
  recommendations_summary?: string;
  forecast_summary?: string;
  related_datasets?: { datasets?: string[] };
  related_jobs?: { jobs?: string[] };
  related_alerts?: { alerts?: string[] };
  resolved_at?: string;
  created_at: string;
  timeline_events: IncidentEvent[];
}
