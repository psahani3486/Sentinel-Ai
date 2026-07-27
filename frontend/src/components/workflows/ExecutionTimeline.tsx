"use client";

import React from "react";
import { WorkflowStepRun } from "@/types/workflow";
import { Clock } from "lucide-react";

interface ExecutionTimelineProps {
  steps: WorkflowStepRun[];
}

export const ExecutionTimeline: React.FC<ExecutionTimelineProps> = ({ steps }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Gantt Execution Duration Timeline
        </h3>
        <p className="text-xs text-slate-500">Step duration breakdown in milliseconds</p>
      </div>

      <div className="space-y-3">
        {steps.map((step) => (
          <div key={step.id || step.step_name} className="space-y-1">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="font-bold text-slate-200">{step.step_name}</span>
              <span className="text-slate-400">{step.execution_time_ms.toFixed(1)} ms</span>
            </div>

            <div className="h-2 w-full rounded-full bg-slate-800 overflow-hidden">
              <div
                className={`h-full rounded-full ${
                  step.state === "completed"
                    ? "bg-emerald-400"
                    : step.state === "failed"
                    ? "bg-rose-400"
                    : "bg-indigo-400"
                }`}
                style={{ width: `${Math.min(100, (step.execution_time_ms / 50.0) * 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
