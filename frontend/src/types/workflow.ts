export interface WorkflowStepRun {
  id: string;
  step_name: string;
  step_type: string;
  state: "pending" | "running" | "completed" | "failed" | "skipped" | "retrying";
  depends_on?: { depends_on?: string[] };
  retry_count: number;
  max_retries: number;
  started_at?: string;
  completed_at?: string;
  execution_time_ms: number;
  logs?: string;
  outputs?: Record<string, any>;
  created_at: string;
}

export interface WorkflowRun {
  id: string;
  dataset_id?: string;
  workflow_type: string;
  state: "created" | "ready" | "running" | "waiting" | "completed" | "failed" | "cancelled" | "skipped";
  title: string;
  total_steps: number;
  completed_steps: number;
  failed_steps: number;
  started_at?: string;
  completed_at?: string;
  execution_time_ms: number;
  context_data?: Record<string, any>;
  created_at: string;
  step_runs: WorkflowStepRun[];
}
