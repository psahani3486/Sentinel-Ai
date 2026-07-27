"use client";

import React from "react";
import { Database, GitBranch, ShieldCheck, ArrowRight, Brain, Zap, LineChart } from "lucide-react";

interface InteractiveLineageGraphProps {
  assetName: string;
}

export const InteractiveLineageGraph: React.FC<InteractiveLineageGraphProps> = ({ assetName }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Interactive Lineage DAG Graph
        </h3>
        <p className="text-xs text-slate-500">Cross-layer dependency graph connecting datasets, workflows, validations, and AI engines</p>
      </div>

      <div className="rounded-lg border border-slate-800 bg-slate-950/80 p-6 flex items-center justify-between overflow-x-auto text-xs font-mono">
        {/* Node 1: Raw Ingestion Stream */}
        <div className="flex flex-col items-center gap-1.5 p-3 rounded-lg border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 font-bold min-w-[120px]">
          <Database className="h-5 w-5" />
          <span>Dataset Asset</span>
          <span className="text-[9px] opacity-75">Raw Telemetry</span>
        </div>

        <ArrowRight className="h-4 w-4 text-slate-600 shrink-0" />

        {/* Node 2: Validation Contract Suite */}
        <div className="flex flex-col items-center gap-1.5 p-3 rounded-lg border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 font-bold min-w-[120px]">
          <ShieldCheck className="h-5 w-5" />
          <span>Validation Suite</span>
          <span className="text-[9px] opacity-75">21 Contracts</span>
        </div>

        <ArrowRight className="h-4 w-4 text-slate-600 shrink-0" />

        {/* Node 3: Airflow Workflow Pipeline */}
        <div className="flex flex-col items-center gap-1.5 p-3 rounded-lg border border-amber-500/30 bg-amber-500/10 text-amber-400 font-bold min-w-[120px]">
          <GitBranch className="h-5 w-5" />
          <span>Workflow DAG</span>
          <span className="text-[9px] opacity-75">E2E Investigation</span>
        </div>

        <ArrowRight className="h-4 w-4 text-slate-600 shrink-0" />

        {/* Node 4: AI Risk Forecast */}
        <div className="flex flex-col items-center gap-1.5 p-3 rounded-lg border border-rose-500/30 bg-rose-500/10 text-rose-400 font-bold min-w-[120px]">
          <LineChart className="h-5 w-5" />
          <span>Risk Forecast</span>
          <span className="text-[9px] opacity-75">OLS Regression</span>
        </div>
      </div>
    </div>
  );
};
