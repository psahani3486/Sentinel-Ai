"use client";

import React from "react";
import { Code, FileText } from "lucide-react";

interface EvidenceViewerProps {
  evidence?: Record<string, any>;
}

export const EvidenceViewer: React.FC<EvidenceViewerProps> = ({ evidence }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-3">
      <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
        <Code className="h-4 w-4 text-indigo-400" /> Evaluation Evidence Telemetry
      </h3>

      <div className="rounded-lg border border-slate-800 bg-slate-950/80 p-4 font-mono text-xs text-indigo-300 overflow-x-auto">
        <pre>{JSON.stringify(evidence || {}, null, 2)}</pre>
      </div>
    </div>
  );
};
