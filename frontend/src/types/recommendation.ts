export interface RecommendationEvidence {
  id: string;
  title: string;
  description: string;
  evidence_payload?: Record<string, any>;
  weight: number;
  created_at: string;
}

export interface Recommendation {
  id: string;
  rca_id?: string;
  dataset_id?: string;
  category: string;
  priority: "critical" | "high" | "medium" | "low" | "info";
  title: string;
  description: string;
  estimated_impact: "HIGH" | "MEDIUM" | "LOW";
  estimated_effort: "LOW" | "MEDIUM" | "HIGH";
  confidence_score: number;
  priority_score: number;
  suggested_next_steps?: { steps?: string[] };
  status: string;
  execution_time_ms: number;
  created_at: string;
  evidences: RecommendationEvidence[];
}
