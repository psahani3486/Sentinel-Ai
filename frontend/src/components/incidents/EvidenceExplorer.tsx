"use client";

import React from "react";
import { IncidentEvent } from "@/types/incident";
import { Database, FileCode, ShieldAlert } from "lucide-react";

interface EvidenceExplorerProps {
  events: IncidentEvent[];
}

export const EvidenceExplorer: React.FC<EvidenceExplorerProps> = ({ events }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Telemetry Evidence Explorer
        </h3>
        <p className="text-xs text-slate-500">JSON telemetry payloads extracted during signal correlation</p>
      </div>

      <div className="space-y-3">
        {events.map((ev) => (
          <div key={ev.id} className="rounded-lg border border-slate-800 bg-slate-950/80 p-4 space-y-2 font-mono text-xs">
            <div className="flex items-center justify-between text-indigo-400 font-bold">
              <span className="flex items-center gap-1.5">
                <FileCode className="h-4 w-4" /> {ev.event_type}
              </span>
              <span className="text-[10px] text-slate-500">{ev.severity}</span>
            </div>

            <pre className="text-[11px] text-slate-300 overflow-x-auto p-2 bg-slate-900/90 rounded border border-slate-800">
              {JSON.stringify(ev.payload || { description: ev.description }, null, 2)}
            </pre>
          </div>
        ))}
      </div>
    </div>
  );
};
