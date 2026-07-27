"use client";

import React from "react";
import { GovernancePolicy } from "@/types/catalog";
import { ShieldCheck, CheckCircle2 } from "lucide-react";

interface GovernanceDashboardProps {
  policies: GovernancePolicy[];
}

export const GovernanceDashboard: React.FC<GovernanceDashboardProps> = ({ policies }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-emerald-400" /> Data Governance Compliance Matrix
        </h3>
        <p className="text-xs text-slate-500">Corporate retention policies, security sensitivity tiers, and audit compliance</p>
      </div>

      <div className="space-y-3">
        {policies.map((p) => (
          <div key={p.id || p.policy_name} className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950/80 p-4 font-mono text-xs">
            <div className="space-y-0.5">
              <span className="font-bold text-slate-100">{p.policy_name}</span>
              <div className="text-[10px] text-slate-500">{p.category}</div>
            </div>

            <span className="inline-flex items-center gap-1 font-bold text-emerald-400 uppercase text-[11px]">
              <CheckCircle2 className="h-3.5 w-3.5" /> {p.compliance_status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
