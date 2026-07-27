"use client";

import React from "react";
import { ShieldCheck, CheckCircle2, AlertTriangle, XCircle } from "lucide-react";

interface ComplianceMatrixProps {
  passCount: number;
  warnCount: number;
  failCount: number;
}

export const ComplianceMatrix: React.FC<ComplianceMatrixProps> = ({ passCount, warnCount, failCount }) => {
  const total = passCount + warnCount + failCount;
  const passPercent = total > 0 ? (passCount / total) * 100 : 100;

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-emerald-400" /> Enterprise Compliance Matrix
        </h3>
        <p className="text-xs text-slate-500">Overall policy evaluation pass rates across 10 governance categories</p>
      </div>

      <div className="grid grid-cols-3 gap-4 text-center font-mono">
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4 space-y-1">
          <CheckCircle2 className="h-5 w-5 mx-auto text-emerald-400" />
          <div className="text-2xl font-extrabold text-emerald-400">{passCount}</div>
          <div className="text-[10px] text-slate-400 uppercase font-bold">Passed Rules</div>
        </div>

        <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-4 space-y-1">
          <AlertTriangle className="h-5 w-5 mx-auto text-amber-400" />
          <div className="text-2xl font-extrabold text-amber-400">{warnCount}</div>
          <div className="text-[10px] text-slate-400 uppercase font-bold">Warning Rules</div>
        </div>

        <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 p-4 space-y-1">
          <XCircle className="h-5 w-5 mx-auto text-rose-400" />
          <div className="text-2xl font-extrabold text-rose-400">{failCount}</div>
          <div className="text-[10px] text-slate-400 uppercase font-bold">Failed Rules</div>
        </div>
      </div>
    </div>
  );
};
