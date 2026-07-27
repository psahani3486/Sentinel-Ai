"use client";

import React from "react";
import { RecommendationEvidence } from "@/types/recommendation";
import { Activity, ShieldAlert } from "lucide-react";

interface EvidencePanelProps {
  evidences: RecommendationEvidence[];
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({ evidences }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Supporting Telemetry Evidence
        </h3>
        <p className="text-xs text-slate-500">Correlated logs and metrics backing recommendation ranking</p>
      </div>

      <div className="space-y-3">
        {evidences.map((ev) => (
          <div key={ev.id} className="rounded-lg border border-slate-800 bg-slate-950/60 p-4 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-indigo-400">{ev.title}</span>
              <span className="font-mono text-[10px] text-slate-500">Weight: {(ev.weight * 100).toFixed(0)}%</span>
            </div>

            <p className="text-xs text-slate-400">{ev.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
