"use client";

import React from "react";
import { Span } from "@/types/telemetry";
import { Clock, CheckCircle2, AlertTriangle, Layers } from "lucide-react";

interface SpanTimelineProps {
  spans: Span[];
  totalDurationMs: number;
}

export const SpanTimeline: React.FC<SpanTimelineProps> = ({ spans, totalDurationMs }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <Layers className="h-4 w-4 text-indigo-400" /> APM Distributed Span Waterfall
        </h3>
        <p className="text-xs text-slate-500">Execution timeline breakdown across microservices, database queries, and AI engines</p>
      </div>

      <div className="space-y-3 font-mono text-xs">
        {spans.map((s, idx) => {
          const widthPercent = Math.max(5, Math.min(100, (s.duration_ms / totalDurationMs) * 100));
          const isChild = Boolean(s.parent_span_id);

          return (
            <div
              key={s.id || s.span_id || idx}
              className={`rounded-lg border p-3 space-y-2 transition-colors ${
                isChild
                  ? "border-slate-800/80 bg-slate-950/60 ml-6"
                  : "border-indigo-500/30 bg-indigo-500/10"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 font-bold">
                  {s.status === "ok" ? (
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  ) : (
                    <AlertTriangle className="h-3.5 w-3.5 text-rose-400" />
                  )}
                  <span className={isChild ? "text-slate-200" : "text-indigo-300"}>
                    {s.name}
                  </span>
                  <span className="text-[10px] text-slate-500">({s.service_name})</span>
                </div>

                <div className="flex items-center gap-1.5 text-indigo-400 font-bold text-xs">
                  <Clock className="h-3 w-3" /> {s.duration_ms.toFixed(1)} ms
                </div>
              </div>

              {/* Waterfall Visual Bar */}
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${
                    isChild ? "bg-indigo-500" : "bg-emerald-400"
                  }`}
                  style={{ width: `${widthPercent}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
