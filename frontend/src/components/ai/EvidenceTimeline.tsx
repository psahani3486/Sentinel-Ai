"use client";

import React from "react";
import { AnalysisEvidence } from "@/types/ai";
import { ShieldAlert, FileText, Activity } from "lucide-react";

interface EvidenceTimelineProps {
  evidences: AnalysisEvidence[];
}

export const EvidenceTimeline: React.FC<EvidenceTimelineProps> = ({ evidences }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Supporting Telemetry Evidence Breakdown
        </h3>
        <p className="text-xs text-slate-500">Deterministic metrics, failed rules, and statistical weights</p>
      </div>

      <div className="space-y-4">
        {evidences.map((ev) => (
          <div key={ev.id} className="rounded-lg border border-slate-800 bg-slate-950/60 p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="inline-flex items-center gap-1 text-[11px] font-bold text-indigo-400 uppercase">
                <Activity className="h-3.5 w-3.5" /> {ev.evidence_type}
              </span>
              <span className="font-mono text-[10px] text-slate-500">Weight: {(ev.weight * 100).toFixed(0)}%</span>
            </div>

            <h4 className="text-xs font-semibold text-slate-200">{ev.title}</h4>
            <p className="text-xs text-slate-400">{ev.description}</p>

            {ev.evidence_payload && (
              <pre className="rounded bg-slate-900 p-2.5 font-mono text-[10px] text-slate-400 overflow-x-auto">
                {JSON.stringify(ev.evidence_payload, null, 2)}
              </pre>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
