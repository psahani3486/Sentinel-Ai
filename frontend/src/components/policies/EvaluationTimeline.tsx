"use client";

import React from "react";
import { PolicyEvaluation } from "@/types/policy";
import { CheckCircle2, AlertTriangle, XCircle, Clock } from "lucide-react";

interface EvaluationTimelineProps {
  evaluations: PolicyEvaluation[];
}

export const EvaluationTimeline: React.FC<EvaluationTimelineProps> = ({ evaluations }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <Clock className="h-4 w-4 text-indigo-400" /> Policy Evaluation Audit Timeline
        </h3>
        <p className="text-xs text-slate-500">Historical evaluation runs across governance, schema, quality, and retention rules</p>
      </div>

      <div className="space-y-3 font-mono text-xs">
        {evaluations.map((ev) => {
          const isPass = ev.status === "pass";
          const isWarn = ev.status === "warning";

          return (
            <div key={ev.id} className="rounded-lg border border-slate-800 bg-slate-950/80 p-4 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 font-bold">
                  {isPass && <CheckCircle2 className="h-4 w-4 text-emerald-400" />}
                  {isWarn && <AlertTriangle className="h-4 w-4 text-amber-400" />}
                  {!isPass && !isWarn && <XCircle className="h-4 w-4 text-rose-400" />}
                  <span className="text-slate-100">{ev.policy_definition?.policy_name || "Enterprise Policy"}</span>
                </div>

                <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold border ${
                  isPass ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" : isWarn ? "bg-amber-500/10 text-amber-400 border-amber-500/30" : "bg-rose-500/10 text-rose-400 border-rose-500/30"
                }`}>
                  {ev.status}
                </span>
              </div>

              <p className="text-slate-300 text-xs font-sans">{ev.recommendation}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
