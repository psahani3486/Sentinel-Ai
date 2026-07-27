"use client";

import React from "react";
import { WorkflowStepRun } from "@/types/workflow";
import { FileCode, Terminal, X } from "lucide-react";

interface StepDetailDrawerProps {
  step: WorkflowStepRun | null;
  onClose: () => void;
}

export const StepDetailDrawer: React.FC<StepDetailDrawerProps> = ({ step, onClose }) => {
  if (!step) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-96 border-l border-slate-800 bg-slate-950/95 p-6 backdrop-blur-md shadow-2xl space-y-6 overflow-y-auto">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h3 className="font-mono font-bold text-indigo-400 text-sm">{step.step_name}</h3>
          <p className="text-[11px] text-slate-500 font-mono">Type: {step.step_type}</p>
        </div>
        <button onClick={onClose} className="rounded p-1 text-slate-400 hover:bg-slate-800">
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Execution Status & Retries */}
      <div className="grid grid-cols-2 gap-4 text-xs font-mono">
        <div className="rounded border border-slate-800 bg-slate-900/60 p-3 space-y-1">
          <span className="text-[10px] text-slate-500 uppercase">State</span>
          <div className="font-bold text-emerald-400 uppercase">{step.state}</div>
        </div>

        <div className="rounded border border-slate-800 bg-slate-900/60 p-3 space-y-1">
          <span className="text-[10px] text-slate-500 uppercase">Retries</span>
          <div className="font-bold text-slate-200">{step.retry_count} / {step.max_retries}</div>
        </div>
      </div>

      {/* Execution Logs */}
      <div className="space-y-2">
        <span className="text-xs font-bold text-slate-300 uppercase flex items-center gap-1.5">
          <Terminal className="h-3.5 w-3.5 text-indigo-400" /> Step Execution Logs
        </span>
        <pre className="p-3 rounded border border-slate-800 bg-slate-900 font-mono text-[11px] text-slate-300 overflow-x-auto whitespace-pre-wrap">
          {step.logs || "No log output recorded for this step."}
        </pre>
      </div>

      {/* Step Outputs JSON */}
      <div className="space-y-2">
        <span className="text-xs font-bold text-slate-300 uppercase flex items-center gap-1.5">
          <FileCode className="h-3.5 w-3.5 text-emerald-400" /> Step Outputs JSON
        </span>
        <pre className="p-3 rounded border border-slate-800 bg-slate-900 font-mono text-[11px] text-slate-300 overflow-x-auto">
          {JSON.stringify(step.outputs || {}, null, 2)}
        </pre>
      </div>
    </div>
  );
};
