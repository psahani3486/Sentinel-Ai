"use client";

import React from "react";
import { CheckCircle2, ArrowRight } from "lucide-react";

interface RecommendedActionsPanelProps {
  actions?: string[];
}

export const RecommendedActionsPanel: React.FC<RecommendedActionsPanelProps> = ({ actions }) => {
  const items = actions && actions.length > 0 ? actions : [
    "Inspect raw input data for unexpected nulls or invalid data types.",
    "Verify upstream ETL transformation steps for broken string-to-numeric casting.",
    "Re-run validation suite after data cleanup.",
  ];

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Recommended Remediation Actions
        </h3>
        <p className="text-xs text-slate-500">Step-by-step resolution workflow suggested by AI RCA Engine</p>
      </div>

      <ul className="space-y-3">
        {items.map((act, idx) => (
          <li key={idx} className="flex items-start gap-3 rounded-lg border border-slate-800 bg-slate-950/60 p-3 text-xs text-slate-300">
            <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
            <span>{act}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
