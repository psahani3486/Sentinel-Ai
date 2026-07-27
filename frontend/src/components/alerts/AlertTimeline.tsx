"use client";

import React from "react";
import { AlertOccurrence } from "@/types/alert";
import { Clock, ShieldAlert } from "lucide-react";

interface AlertTimelineProps {
  occurrences: AlertOccurrence[];
}

export const AlertTimeline: React.FC<AlertTimelineProps> = ({ occurrences }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Incident Occurrence Timeline & Escalation History
        </h3>
        <p className="text-xs text-slate-500">Historical deduplicated telemetry occurrences</p>
      </div>

      <div className="relative border-l-2 border-slate-800 ml-4 pl-6 space-y-6">
        {occurrences.map((occ, idx) => (
          <div key={occ.id || idx} className="relative">
            {/* Timeline Dot */}
            <span className="absolute -left-[31px] top-1 h-3 w-3 rounded-full bg-indigo-500 ring-4 ring-slate-900" />

            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono text-indigo-400 font-semibold">
                  Occurrence #{occurrences.length - idx}
                </span>
                <span className="flex items-center gap-1 font-mono text-slate-500">
                  <Clock className="h-3 w-3" /> {new Date(occ.created_at).toLocaleString()}
                </span>
              </div>

              <p className="text-xs text-slate-300">{occ.message}</p>

              {occ.event_payload && (
                <pre className="rounded bg-slate-900 p-2.5 font-mono text-[10px] text-slate-400 overflow-x-auto">
                  {JSON.stringify(occ.event_payload, null, 2)}
                </pre>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
