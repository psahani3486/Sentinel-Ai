"use client";

import React from "react";
import { CheckCircle2, ArrowRight } from "lucide-react";

interface ActionChecklistProps {
  steps?: string[];
}

export const ActionChecklist: React.FC<ActionChecklistProps> = ({ steps }) => {
  const list = steps && steps.length > 0 ? steps : [
    "Filter or cast unparseable string values prior to SQL database insert.",
    "Update validation rule parameters to tolerate expected operational noise bounds.",
    "Trigger automated validation suite re-run.",
  ];

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Step-by-Step Remediation Action Plan
        </h3>
        <p className="text-xs text-slate-500">Ordered execution checklist for operations team</p>
      </div>

      <ul className="space-y-3">
        {list.map((step, idx) => (
          <li key={idx} className="flex items-start gap-3 rounded-lg border border-slate-800 bg-slate-950/60 p-3.5 text-xs text-slate-300">
            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-indigo-500/20 font-mono text-[10px] font-bold text-indigo-400 border border-indigo-500/30">
              {idx + 1}
            </span>
            <span className="mt-0.5">{step}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
