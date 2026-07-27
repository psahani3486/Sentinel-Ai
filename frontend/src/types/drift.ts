export interface DriftResult {
  id: string;
  column_name: string;
  column_type: string;
  detector_type: string;
  drift_detected: boolean;
  drift_score: number;
  threshold: number;
  severity: "critical" | "high" | "medium" | "low" | "info";
  explanation: string;
  metrics_data?: Record<string, any>;
}

export interface DriftRun {
  id: string;
  dataset_id: string;
  current_version_id: string;
  baseline_version_id: string;
  status: "no_drift" | "low" | "medium" | "high" | "critical";
  overall_drift_score: number;
  drifted_columns_count: number;
  total_columns_analyzed: number;
  execution_time_ms: number;
  summary?: Record<string, any>;
  results: DriftResult[];
}
