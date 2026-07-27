"use client";

import React from "react";
import { Database, AlertTriangle, Cpu, Brain, Zap, LineChart } from "lucide-react";

interface CorrelationGraphProps {
  title: string;
}

export const CorrelationGraph: React.FC<CorrelationGraphProps> = ({ title }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Telemetry Signal Correlation Graph
        </h3>
        <p className="text-xs text-slate-500">Node graph mapping cross-layer platform signals to root cause</p>
      </div>

      {/* Visual Graph Diagram */}
      <div className="rounded-lg border border-slate-800 bg-slate-950/80 p-6 flex items-center justify-between overflow-x-auto text-xs">
        {/* Node 1: Dataset */}
        <div className="flex flex-col items-center gap-1.5 p-3 rounded-lg border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 font-bold min-w-[100px]">
          <Database className="h-5 w-5" />
          <span>Dataset Asset</span>
        </div>

        <div className="h-0.5 w-12 bg-slate-800" />

        {/* Node 2: Alert */}
        <div className="flex flex-col items-center gap-1.5 p-3 rounded-lg border border-rose-500/30 bg-rose-500/10 text-rose-400 font-bold min-w-[100px]">
          <AlertTriangle className="h-5 w-5" />
          <span>Active Alert</span>
        </div>

        <div className="h-0.5 w-12 bg-slate-800" />

        {/* Node 3: AI RCA */}
        <div className="flex flex-col items-center gap-1.5 p-3 rounded-lg border border-amber-500/30 bg-amber-500/10 text-amber-400 font-bold min-w-[100px]">
          <Brain className="h-5 w-5" />
          <span>AI Root Cause</span>
        </div>

        <div className="h-0.5 w-12 bg-slate-800" />

        {/* Node 4: Recommendation */}
        <div className="flex flex-col items-center gap-1.5 p-3 rounded-lg border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 font-bold min-w-[100px]">
          <Zap className="h-5 w-5" />
          <span>Action Plan</span>
        </div>
      </div>
    </div>
  );
};
