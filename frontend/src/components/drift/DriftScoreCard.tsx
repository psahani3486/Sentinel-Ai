"use client";

import React from "react";
import { AlertOctagon, CheckCircle2, AlertTriangle, Info } from "lucide-react";

interface DriftScoreCardProps {
  score: number;
  status: string;
  driftedColumnsCount: number;
  totalColumnsAnalyzed: number;
}

export const DriftScoreCard: React.FC<DriftScoreCardProps> = ({
  score,
  status,
  driftedColumnsCount,
  totalColumnsAnalyzed,
}) => {
  const getStatusColor = () => {
    switch (status.toLowerCase()) {
      case "no_drift":
        return "text-emerald-400 bg-emerald-500/10 border-emerald-500/20";
      case "low":
        return "text-sky-400 bg-sky-500/10 border-sky-500/20";
      case "medium":
        return "text-amber-400 bg-amber-500/10 border-amber-500/20";
      case "high":
      case "critical":
        return "text-rose-400 bg-rose-500/10 border-rose-500/20";
      default:
        return "text-slate-400 bg-slate-500/10 border-slate-500/20";
    }
  };

  const getStatusIcon = () => {
    switch (status.toLowerCase()) {
      case "no_drift":
        return <CheckCircle2 className="h-5 w-5 text-emerald-400" />;
      case "low":
      case "medium":
        return <AlertTriangle className="h-5 w-5 text-amber-400" />;
      case "high":
      case "critical":
        return <AlertOctagon className="h-5 w-5 text-rose-400" />;
      default:
        return <Info className="h-5 w-5 text-slate-400" />;
    }
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg flex items-center justify-between">
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold border uppercase tracking-wider ${getStatusColor()}`}>
            {getStatusIcon()} {status.replace("_", " ")}
          </span>
          <span className="text-xs text-slate-400">
            {driftedColumnsCount} of {totalColumnsAnalyzed} columns drifted
          </span>
        </div>
        <h2 className="text-2xl font-extrabold text-white">Overall Dataset Drift Ratio</h2>
        <p className="text-xs text-slate-500">
          Evaluated across 10 statistical drift algorithms (PSI, JS-Divergence, Wasserstein, Mean Shift).
        </p>
      </div>

      <div className="text-right space-y-1">
        <div className="text-4xl font-extrabold tracking-tight text-indigo-400 font-mono">
          {score.toFixed(1)}%
        </div>
        <span className="text-[11px] uppercase tracking-wider text-slate-500 font-semibold block">
          Feature Drift Index
        </span>
      </div>
    </div>
  );
};
