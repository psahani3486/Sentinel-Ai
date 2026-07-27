export interface CatalogLineage {
  id: string;
  source_asset_id: string;
  target_asset_id: string;
  relationship_type: string;
  lineage_dag?: Record<string, any>;
  created_at: string;
}

export interface CatalogAsset {
  id: string;
  dataset_id?: string;
  name: string;
  asset_type: "dataset" | "table" | "column" | "pipeline" | "model" | "dashboard";
  domain: string;
  owner: string;
  steward: string;
  business_description: string;
  technical_description: string;
  sensitivity: "public" | "internal" | "confidential" | "restricted" | "pii";
  retention_period_days: number;
  lifecycle_status: "proposed" | "active" | "deprecated" | "archived";
  tags?: { tags?: string[] };
  classifications?: { classifications?: string[] };
  created_at: string;
  outgoing_lineages: CatalogLineage[];
  incoming_lineages: CatalogLineage[];
}

export interface GlossaryTerm {
  id: string;
  term: string;
  definition: string;
  domain: string;
  related_assets?: { assets?: string[] };
  created_at: string;
}

export interface GovernancePolicy {
  id: string;
  policy_name: string;
  category: string;
  rules_definition?: Record<string, any>;
  compliance_status: string;
  created_at: string;
}
