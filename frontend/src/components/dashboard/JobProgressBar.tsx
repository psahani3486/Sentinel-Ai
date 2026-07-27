"use client";

import React from "react";
import { Loader2, CheckCircle2, XCircle, Clock } from "lucide-react";

interface JobProgressBarProps {
  jobId: string;
  jobType: string;
  status: string;
  progressPercentage: number;
  message?: string;
  executionTimeMs?: number;
}

export const JobProgressBar: React.FC<JobProgressBarProps> = ({
  jobId,
  jobType,
  status,
  progressPercentage,
  message,
  executionTimeMs,
}) => {
  const normProgress = Math.max(0, Math.min(100, progressPercentage));

  const getStatusIcon = () => {
    switch (status.toLowerCase()) {
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-emerald-400" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-rose-400" />;
      case "running":
      case "queued":
        return <Loader2 className="h-4 w-4 text-indigo-400 animate-spin" />;
      default:
        return <Clock className="h-4 w-4 text-amber-400" />;
    }
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4 space-y-3 shadow-md">
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-2 font-mono font-semibold text-slate-200">
          {getStatusIcon()}
          <span>{jobType.toUpperCase()}</span>
          <span className="text-slate-500">• {jobId}</span>
        </div>
        <span className="font-mono font-bold text-indigo-400">{normProgress.toFixed(0)}%</span>
      </div>

      {/* Progress Track */}
      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 transition-all duration-500 ease-out"
          style={{ width: `${normProgress}%` }}
        />
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-400">
        <span className="truncate max-w-md">{message || "Processing task..."}</span>
        {executionTimeMs !== undefined && executionTimeMs > 0 && (
          <span className="font-mono">{executionTimeMs.toFixed(1)} ms</span>
        )}
      </div>
    </div>
  );
};
