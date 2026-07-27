export interface AnalysisEvidence {
  id: string;
  evidence_type: string;
  title: string;
  description: string;
  evidence_payload?: Record<string, any>;
  weight: number;
  created_at: string;
}

export interface RootCauseAnalysis {
  id: string;
  analysis_type: string;
  target_entity_type: string;
  target_entity_id: string;
  dataset_id?: string;
  summary: string;
  probable_root_cause: string;
  confidence_score: number;
  severity: "critical" | "high" | "medium" | "low" | "info";
  affected_components?: { components?: string[] };
  recommended_actions?: { actions?: string[] };
  status: "pending" | "completed" | "failed";
  execution_time_ms: number;
  llm_provider_name: string;
  created_at: string;
  evidences: AnalysisEvidence[];
}
