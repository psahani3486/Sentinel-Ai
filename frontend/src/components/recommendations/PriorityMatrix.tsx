"use client";

import React from "react";
import { Recommendation } from "@/types/recommendation";
import { Zap, Target, AlertTriangle, ShieldCheck } from "lucide-react";

interface PriorityMatrixProps {
  recommendations: Recommendation[];
}

export const PriorityMatrix: React.FC<PriorityMatrixProps> = ({ recommendations }) => {
  const quickWins = recommendations.filter(
    (r) => r.estimated_impact === "HIGH" && r.estimated_effort === "LOW"
  );
  const majorProjects = recommendations.filter(
    (r) => r.estimated_impact === "HIGH" && r.estimated_effort !== "LOW"
  );
  const fillIns = recommendations.filter(
    (r) => r.estimated_impact !== "HIGH" && r.estimated_effort === "LOW"
  );
  const thanklessTasks = recommendations.filter(
    (r) => r.estimated_impact !== "HIGH" && r.estimated_effort !== "LOW"
  );

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Remediation Priority Matrix (2x2 Impact vs Effort)
        </h3>
        <p className="text-xs text-slate-500">Prioritized quadrant allocation based on weighted scoring algorithm</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Quadrant 1: Quick Wins */}
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase text-emerald-400 flex items-center gap-1">
              <Zap className="h-3.5 w-3.5" /> Quick Wins (High Impact, Low Effort)
            </span>
            <span className="font-mono text-xs font-bold text-emerald-400">{quickWins.length}</span>
          </div>
          <p className="text-[11px] text-slate-300">Top-priority actions with maximum ROI and instant deployment.</p>
        </div>

        {/* Quadrant 2: Major Projects */}
        <div className="rounded-lg border border-indigo-500/30 bg-indigo-500/10 p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase text-indigo-400 flex items-center gap-1">
              <Target className="h-3.5 w-3.5" /> Major Projects (High Impact, High Effort)
            </span>
            <span className="font-mono text-xs font-bold text-indigo-400">{majorProjects.length}</span>
          </div>
          <p className="text-[11px] text-slate-300">High strategic value requiring schema migration or architecture refactoring.</p>
        </div>

        {/* Quadrant 3: Fill-ins */}
        <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase text-amber-400 flex items-center gap-1">
              <ShieldCheck className="h-3.5 w-3.5" /> Quick Tasks (Low Impact, Low Effort)
            </span>
            <span className="font-mono text-xs font-bold text-amber-400">{fillIns.length}</span>
          </div>
          <p className="text-[11px] text-slate-300">Minor threshold tuning or alert suppression configuration.</p>
        </div>

        {/* Quadrant 4: De-prioritized */}
        <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase text-slate-400 flex items-center gap-1">
              <AlertTriangle className="h-3.5 w-3.5" /> De-prioritized (Low Impact, High Effort)
            </span>
            <span className="font-mono text-xs font-bold text-slate-400">{thanklessTasks.length}</span>
          </div>
          <p className="text-[11px] text-slate-400">Low urgency actions to schedule during scheduled maintenance windows.</p>
        </div>
      </div>
    </div>
  );
};
