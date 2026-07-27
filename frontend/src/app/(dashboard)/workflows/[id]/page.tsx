"use client";

import React, { useState } from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, GitBranch } from "lucide-react";
import { WorkflowStepRun } from "@/types/workflow";
import { DAGVisualization } from "@/components/workflows/DAGVisualization";
import { ExecutionTimeline } from "@/components/workflows/ExecutionTimeline";
import { StepDetailDrawer } from "@/components/workflows/StepDetailDrawer";
import Link from "next/link";

export default function WorkflowDetailPage() {
  const params = useParams();
  const runId = params.id as string;

  const [selectedStep, setSelectedStep] = useState<WorkflowStepRun | null>(null);

  const mockSteps: WorkflowStepRun[] = [
    {
      id: "s-1",
      step_name: "ingest",
      step_type: "DatasetIngest",
      state: "completed",
      retry_count: 0,
      max_retries: 3,
      execution_time_ms: 12.5,
      logs: "Connecting to CSV data connector...\nLoaded 1,000 sensor observations.\nDataset ingestion complete.",
      outputs: { records: 1000, dataset_id: "ds-1" },
      created_at: "2026-07-26T14:45:00Z",
    },
    {
      id: "s-2",
      step_name: "profile",
      step_type: "DatasetProfile",
      state: "completed",
      depends_on: { depends_on: ["ingest"] },
      retry_count: 0,
      max_retries: 3,
      execution_time_ms: 8.2,
      logs: "Computing column statistics...\nExtracted metadata for 12 columns.",
      outputs: { columns_profiled: 12 },
      created_at: "2026-07-26T14:45:01Z",
    },
    {
      id: "s-3",
      step_name: "validate",
      step_type: "DatasetValidate",
      state: "completed",
      depends_on: { depends_on: ["ingest"] },
      retry_count: 0,
      max_retries: 3,
      execution_time_ms: 14.1,
      logs: "Evaluating validation rule suite...\nRule 'missing_values' failed on sensor_temp.",
      outputs: { rules_passed: 18, rules_failed: 1 },
      created_at: "2026-07-26T14:45:02Z",
    },
    {
      id: "s-4",
      step_name: "drift",
      step_type: "DriftDetect",
      state: "completed",
      depends_on: { depends_on: ["profile"] },
      retry_count: 0,
      max_retries: 3,
      execution_time_ms: 6.8,
      logs: "Calculating Population Stability Index...\nDrift detected (PSI: 0.18).",
      outputs: { psi: 0.18 },
      created_at: "2026-07-26T14:45:03Z",
    },
    {
      id: "s-5",
      step_name: "alerts",
      step_type: "AlertEvaluate",
      state: "completed",
      depends_on: { depends_on: ["validate"] },
      retry_count: 0,
      max_retries: 3,
      execution_time_ms: 4.5,
      logs: "Evaluating alert rules...\nTriggered Quality Score Drop alert.",
      outputs: { alert_id: "alt-1" },
      created_at: "2026-07-26T14:45:04Z",
    },
    {
      id: "s-6",
      step_name: "rca",
      step_type: "RootCauseAnalyze",
      state: "completed",
      depends_on: { depends_on: ["validate", "alerts"] },
      retry_count: 0,
      max_retries: 3,
      execution_time_ms: 15.3,
      logs: "Gathering telemetry context...\nSynthesized AI Root Cause explanation.",
      outputs: { root_cause: "Malformed pre-ingestion strings", confidence: 92.5 },
      created_at: "2026-07-26T14:45:05Z",
    },
    {
      id: "s-7",
      step_name: "recommendation",
      step_type: "RecommendationGenerate",
      state: "completed",
      depends_on: { depends_on: ["rca"] },
      retry_count: 0,
      max_retries: 3,
      execution_time_ms: 9.1,
      logs: "Evaluating remediation strategies...\nCalculated priority score: 91.8.",
      outputs: { priority_score: 91.8 },
      created_at: "2026-07-26T14:45:06Z",
    },
    {
      id: "s-8",
      step_name: "incident",
      step_type: "IncidentCorrelate",
      state: "completed",
      depends_on: { depends_on: ["rca", "recommendation"] },
      retry_count: 0,
      max_retries: 3,
      execution_time_ms: 7.4,
      logs: "Correlating platform signals...\nCreated Incident Workspace.",
      outputs: { incident_id: "inc-1" },
      created_at: "2026-07-26T14:45:07Z",
    },
    {
      id: "s-9",
      step_name: "forecast",
      step_type: "RiskForecast",
      state: "completed",
      depends_on: { depends_on: ["drift", "incident"] },
      retry_count: 0,
      max_retries: 3,
      execution_time_ms: 10.2,
      logs: "Fitting Ordinary Least Squares regression model...\nProjected quality score recovery in 7 days.",
      outputs: { projected_quality_score: 82.5 },
      created_at: "2026-07-26T14:45:08Z",
    },
  ];

  return (
    <div className="space-y-8 p-8">
      {/* Navigation Header */}
      <div>
        <Link
          href="/workflows"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:underline mb-2"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Workflow Dashboard
        </Link>
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            End-to-End Investigation DAG Execution
          </h1>
          <span className="font-mono text-xs text-slate-500">• {runId}</span>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Workflow Type</p>
          <div className="text-xl font-extrabold font-mono text-indigo-400">END_TO_END_INVESTIGATION</div>
          <p className="text-xs text-slate-500">Full 9-step DAG pipeline</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Execution State</p>
          <div className="text-3xl font-extrabold font-mono text-emerald-400">COMPLETED</div>
          <p className="text-xs text-slate-500">All steps succeeded</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Steps Progress</p>
          <div className="text-3xl font-extrabold font-mono text-white">9 / 9</div>
          <p className="text-xs text-slate-500">0 failed steps</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Execution Time</p>
          <div className="text-3xl font-extrabold font-mono text-slate-300">98.1ms</div>
          <p className="text-xs text-slate-500">Parallel DAG resolution</p>
        </div>
      </div>

      {/* DAG Visualization */}
      <DAGVisualization steps={mockSteps} onSelectStep={(s) => setSelectedStep(s)} />

      {/* Gantt Timeline */}
      <ExecutionTimeline steps={mockSteps} />

      {/* Step Detail Drawer */}
      <StepDetailDrawer step={selectedStep} onClose={() => setSelectedStep(null)} />
    </div>
  );
}
