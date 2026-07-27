export interface AlertOccurrence {
  id: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  message: string;
  event_payload?: Record<string, any>;
  created_at: string;
}

export interface Alert {
  id: string;
  fingerprint: string;
  dataset_id?: string;
  alert_type: string;
  status: "open" | "acknowledged" | "resolved" | "suppressed";
  severity: "critical" | "high" | "medium" | "low" | "info";
  title: string;
  description: string;
  occurrence_count: number;
  first_seen_at: string;
  last_seen_at: string;
  acknowledged_at?: string;
  acknowledged_by_id?: string;
  resolved_at?: string;
  resolved_by_id?: string;
  alert_metadata?: Record<string, any>;
  occurrences: AlertOccurrence[];
}
