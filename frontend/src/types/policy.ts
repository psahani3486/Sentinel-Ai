export interface PolicyDefinition {
  id: string;
  policy_name: string;
  category: "dataset_governance" | "schema" | "validation" | "quality_threshold" | "drift_threshold" | "workflow" | "plugin" | "catalog_governance" | "retention" | "incident_escalation";
  severity: "critical" | "high" | "medium" | "low" | "info";
  description: string;
  rules_spec?: Record<string, any>;
  is_active: boolean;
  created_at: string;
}

export interface PolicyEvaluation {
  id: string;
  policy_id: string;
  status: "pass" | "fail" | "warning";
  severity: "critical" | "high" | "medium" | "low" | "info";
  evidence?: Record<string, any>;
  recommendation: string;
  evaluated_at: string;
  policy_definition?: PolicyDefinition;
}
