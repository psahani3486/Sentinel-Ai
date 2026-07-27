"use client";

import React from "react";
import { WorkflowStepRun } from "@/types/workflow";
import { CheckCircle2, AlertCircle, Clock, Play, ArrowRight } from "lucide-react";

interface DAGVisualizationProps {
  steps: WorkflowStepRun[];
  onSelectStep?: (step: WorkflowStepRun) => void;
}

export const DAGVisualization: React.FC<DAGVisualizationProps> = ({ steps, onSelectStep }) => {
  const getStepColor = (state: string) => {
    switch (state) {
      case "completed":
        return "border-emerald-500/40 bg-emerald-500/10 text-emerald-400";
      case "failed":
        return "border-rose-500/40 bg-rose-500/10 text-rose-400";
      case "running":
        return "border-indigo-500/40 bg-indigo-500/10 text-indigo-400 animate-pulse";
      default:
        return "border-slate-800 bg-slate-950/60 text-slate-400";
    }
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Interactive DAG Dependency Graph
        </h3>
        <p className="text-xs text-slate-500">Node visualization of step dependencies and real-time execution states</p>
      </div>

      <div className="flex items-center gap-3 overflow-x-auto p-4 bg-slate-950/80 rounded-lg border border-slate-800">
        {steps.map((step, idx) => (
          <React.Fragment key={step.id || step.step_name}>
            <button
              onClick={() => onSelectStep && onSelectStep(step)}
              className={`flex flex-col items-center gap-1.5 p-3.5 rounded-lg border font-mono text-xs transition-all hover:scale-105 min-w-[120px] ${getStepColor(
                step.state
              )}`}
            >
              <div className="flex items-center gap-1 font-bold">
                {step.state === "completed" && <CheckCircle2 className="h-4 w-4 text-emerald-400" />}
                {step.state === "failed" && <AlertCircle className="h-4 w-4 text-rose-400" />}
                {step.state === "running" && <Play className="h-4 w-4 text-indigo-400" />}
                {step.state === "pending" && <Clock className="h-4 w-4 text-slate-500" />}
                <span>{step.step_name}</span>
              </div>
              <span className="text-[10px] opacity-80 uppercase tracking-tight">{step.state}</span>
            </button>

            {idx < steps.length - 1 && <ArrowRight className="h-4 w-4 text-slate-600 shrink-0" />}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};
