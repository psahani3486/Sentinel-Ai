export type ValidationStatus = "passed" | "failed" | "warning" | "error" | "pending";

export type ValidationSeverity = "critical" | "high" | "medium" | "low";

export interface RuleResultItem {
  id: string;
  rule_type: string;
  status: ValidationStatus;
  severity: ValidationSeverity;
  message: string;
  affected_columns?: string[];
  affected_rows_count?: number;
  execution_time_ms: number;
  score_impact: number;
  details?: Record<string, any>;
}

export interface ValidationRunItem {
  id: string;
  dataset_id: string;
  dataset_version_id: string;
  status: ValidationStatus;
  overall_score: number;
  completeness_score?: number;
  consistency_score?: number;
  accuracy_score?: number;
  freshness_score?: number;
  execution_time_ms: number;
  created_at: string;
  results?: RuleResultItem[];
}

export interface ValidationHistoryResponse {
  dataset_id: string;
  items: ValidationRunItem[];
  total: number;
  page: number;
  limit: number;
}

export interface ValidationRuleMetadata {
  rule_type: string;
  name: string;
  description: string;
  category: string;
  severity: ValidationSeverity;
}

export interface RuleRegistryResponse {
  total_rules: number;
  rules: ValidationRuleMetadata[];
}
