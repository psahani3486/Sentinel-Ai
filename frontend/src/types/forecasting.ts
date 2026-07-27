export interface ForecastResult {
  id: string;
  target_metric: string;
  predicted_value: number;
  confidence_interval_lower: number;
  confidence_interval_upper: number;
  trend_direction: "upward" | "downward" | "stable";
  risk_level: "critical" | "high" | "medium" | "low" | "info";
  explanation: string;
  preventive_actions?: { actions?: string[] };
  created_at: string;
}

export interface ForecastRun {
  id: string;
  dataset_id?: string;
  forecast_type: string;
  algorithm_name: string;
  forecast_horizon_days: number;
  overall_risk_level: "critical" | "high" | "medium" | "low" | "info";
  summary: string;
  execution_time_ms: number;
  status: string;
  created_at: string;
  results: ForecastResult[];
}
