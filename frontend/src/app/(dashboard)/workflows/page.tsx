"use client";

import React, { useState } from "react";
import { WorkflowRun } from "@/types/workflow";
import { GitBranch, Play, CheckCircle2, AlertCircle, Filter, ArrowUpRight } from "lucide-react";
import Link from "next/link";

export default function WorkflowDashboardPage() {
  const [filterState, setFilterState] = useState<string>("all");

  const [workflowRuns, setWorkflowRuns] = useState<WorkflowRun[]>([
    {
      id: "wf-101",
      workflow_type: "end_to_end_investigation",
      state: "completed",
      title: "End-to-End Incident Investigation Pipeline",
      total_steps: 9,
      completed_steps: 9,
      failed_steps: 0,
      execution_time_ms: 48.5,
      created_at: "2026-07-26T14:45:00Z",
      step_runs: [],
    },
    {
      id: "wf-102",
      workflow_type: "validation",
      state: "completed",
      title: "Automated Data Validation Contract Execution",
      total_steps: 3,
      completed_steps: 3,
      failed_steps: 0,
      execution_time_ms: 18.2,
      created_at: "2026-07-26T14:00:00Z",
      step_runs: [],
    },
    {
      id: "wf-103",
      workflow_type: "drift_detection",
      state: "completed",
      title: "Feature Distribution Drift Pipeline",
      total_steps: 3,
      completed_steps: 3,
      failed_steps: 0,
      execution_time_ms: 15.1,
      created_at: "2026-07-26T13:30:00Z",
      step_runs: [],
    },
  ]);

  const filtered = workflowRuns.filter((w) => {
    if (filterState !== "all" && w.state !== filterState) return false;
    return true;
  });

  return (
    <div className="space-y-8 p-8">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              Enterprise Workflow Orchestration Engine
            </h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
              <GitBranch className="h-3.5 w-3.5" /> 10 Built-in DAG Pipelines
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Coordinates Ingestion, Profiling, Validation, Drift Detection, Alerting, RCA, Recommendations, Forecasts, and Incidents into DAG execution pipelines.
          </p>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Workflow Runs</p>
          <div className="text-3xl font-extrabold font-mono text-white">3</div>
          <p className="text-xs text-slate-500">All pipeline executions</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Completed Runs</p>
          <div className="text-3xl font-extrabold font-mono text-emerald-400">3</div>
          <p className="text-xs text-slate-500">100% success rate</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Active DAG Steps</p>
          <div className="text-3xl font-extrabold font-mono text-indigo-400">15</div>
          <p className="text-xs text-slate-500">Total step executions</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Avg DAG Latency</p>
          <div className="text-3xl font-extrabold font-mono text-slate-300">27.2ms</div>
          <p className="text-xs text-slate-500">Fast parallel execution</p>
        </div>
      </div>

      {/* Filters & Workflow Log */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <h2 className="text-lg font-bold text-white">Workflow Execution History</h2>

        <div className="flex items-center gap-3">
          <Filter className="h-4 w-4 text-slate-400" />
          <select
            value={filterState}
            onChange={(e) => setFilterState(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none"
          >
            <option value="all">All States</option>
            <option value="completed">Completed</option>
            <option value="running">Running</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-lg overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="border-b border-slate-800 bg-slate-950/60 uppercase font-bold text-slate-400">
            <tr>
              <th className="py-3.5 px-4">Workflow Type</th>
              <th className="py-3.5 px-4">Pipeline Title</th>
              <th className="py-3.5 px-4 font-center">State</th>
              <th className="py-3.5 px-4 text-center">Progress (Steps)</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {filtered.map((run) => (
              <tr key={run.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3.5 px-4 font-mono font-bold text-indigo-400 uppercase">{run.workflow_type}</td>
                <td className="py-3.5 px-4 font-semibold text-slate-100">{run.title}</td>
                <td className="py-3.5 px-4 uppercase font-mono font-bold text-emerald-400">{run.state}</td>
                <td className="py-3.5 px-4 text-center font-mono font-bold text-slate-300">
                  {run.completed_steps} / {run.total_steps} Steps
                </td>
                <td className="py-3.5 px-4 text-right">
                  <Link
                    href={`/workflows/${run.id}`}
                    className="rounded border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-[11px] font-semibold text-indigo-400 hover:bg-indigo-500/20 inline-block"
                  >
                    View DAG <ArrowUpRight className="h-3 w-3 inline" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
