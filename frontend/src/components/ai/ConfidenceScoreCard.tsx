"use client";

import React from "react";
import { Cpu, ShieldCheck } from "lucide-react";

interface ConfidenceScoreCardProps {
  score: number;
  providerName: string;
  executionTimeMs: number;
}

export const ConfidenceScoreCard: React.FC<ConfidenceScoreCardProps> = ({
  score,
  providerName,
  executionTimeMs,
}) => {
  const getScoreColor = (val: number) => {
    if (val >= 90) return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10";
    if (val >= 75) return "text-indigo-400 border-indigo-500/30 bg-indigo-500/10";
    return "text-amber-400 border-amber-500/30 bg-amber-500/10";
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400">
          <Cpu className="h-4 w-4 text-indigo-400" /> AI Diagnostic Confidence Index
        </span>
        <span className="font-mono text-[11px] text-slate-500">{providerName} • {executionTimeMs.toFixed(1)}ms</span>
      </div>

      <div className="flex items-baseline gap-4">
        <div className={`text-4xl font-extrabold font-mono rounded-xl px-4 py-2 border ${getScoreColor(score)}`}>
          {score.toFixed(1)}%
        </div>
        <div>
          <p className="text-xs font-semibold text-slate-200">Statistical Match Index</p>
          <p className="text-[11px] text-slate-400">
            {score >= 90
              ? "High diagnostic certainty based on multi-source correlated telemetry."
              : "Moderate diagnostic certainty. Review recommended remediation steps."}
          </p>
        </div>
      </div>
    </div>
  );
};
