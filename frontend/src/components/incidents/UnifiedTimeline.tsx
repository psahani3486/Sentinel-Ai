"use client";

import React from "react";
import { IncidentEvent } from "@/types/incident";
import { Clock, AlertTriangle, ArrowUpRight, Activity } from "lucide-react";
import Link from "next/link";

interface UnifiedTimelineProps {
  events: IncidentEvent[];
}

export const UnifiedTimeline: React.FC<UnifiedTimelineProps> = ({ events }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-6">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Chronological Investigation Timeline
        </h3>
        <p className="text-xs text-slate-500">Correlated platform telemetry events ordered chronologically</p>
      </div>

      <div className="relative border-l-2 border-slate-800 ml-4 pl-6 space-y-6">
        {events.map((ev) => (
          <div key={ev.id} className="relative group">
            {/* Timeline Circle Bullet */}
            <div className="absolute -left-[31px] top-1 h-3.5 w-3.5 rounded-full border-2 border-indigo-500 bg-slate-950 shadow-md shadow-indigo-500/50" />

            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4 space-y-2 hover:border-slate-700 transition-colors">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-indigo-400 uppercase flex items-center gap-1.5">
                  <Activity className="h-3.5 w-3.5 text-indigo-400" /> {ev.event_type}
                </span>
                <span className="font-mono text-[11px] text-slate-500 flex items-center gap-1">
                  <Clock className="h-3 w-3" /> {new Date(ev.timestamp).toLocaleTimeString()}
                </span>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">{ev.description}</p>

              {ev.evidence_link && (
                <div className="pt-1">
                  <Link
                    href={ev.evidence_link}
                    className="inline-flex items-center gap-1 text-[11px] font-semibold text-indigo-400 hover:underline"
                  >
                    View Correlated Artifact <ArrowUpRight className="h-3 w-3" />
                  </Link>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
