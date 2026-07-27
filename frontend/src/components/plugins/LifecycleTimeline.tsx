"use client";

import React from "react";
import { CheckCircle2, ArrowRight } from "lucide-react";

interface LifecycleTimelineProps {
  currentStatus: string;
}

export const LifecycleTimeline: React.FC<LifecycleTimelineProps> = ({ currentStatus }) => {
  const stages = ["discovered", "validated", "loaded", "enabled"];

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Plugin Lifecycle State Machine
        </h3>
        <p className="text-xs text-slate-500">Local plugin discovery and loading state transitions</p>
      </div>

      <div className="flex items-center gap-3 overflow-x-auto p-4 bg-slate-950/80 rounded-lg border border-slate-800 text-xs font-mono">
        {stages.map((stg, idx) => (
          <React.Fragment key={stg}>
            <div className="flex items-center gap-1.5 p-2.5 rounded bg-slate-900 border border-slate-800 text-indigo-400 font-bold uppercase">
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
              <span>{stg}</span>
            </div>

            {idx < stages.length - 1 && <ArrowRight className="h-4 w-4 text-slate-600 shrink-0" />}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};
