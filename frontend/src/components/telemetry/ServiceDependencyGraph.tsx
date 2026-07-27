"use client";

import React from "react";
import { Activity, ArrowRight, Database, Cpu, ShieldCheck, Zap } from "lucide-react";

export const ServiceDependencyGraph: React.FC = () => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <Activity className="h-4 w-4 text-emerald-400" /> Platform Subsystem Service Mesh Graph
        </h3>
        <p className="text-xs text-slate-500">Live operational topology and health status of internal platform components</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-6 gap-3 font-mono text-xs text-center">
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 space-y-1">
          <Zap className="h-5 w-5 mx-auto text-emerald-400" />
          <div className="font-bold text-slate-200">FastAPI API</div>
          <div className="text-[9px] text-emerald-400 uppercase font-bold">HEALTHY</div>
        </div>

        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 space-y-1">
          <Database className="h-5 w-5 mx-auto text-emerald-400" />
          <div className="font-bold text-slate-200">PostgreSQL</div>
          <div className="text-[9px] text-emerald-400 uppercase font-bold">HEALTHY</div>
        </div>

        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 space-y-1">
          <Activity className="h-5 w-5 mx-auto text-emerald-400" />
          <div className="font-bold text-slate-200">Redis Broker</div>
          <div className="text-[9px] text-emerald-400 uppercase font-bold">HEALTHY</div>
        </div>

        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 space-y-1">
          <Cpu className="h-5 w-5 mx-auto text-emerald-400" />
          <div className="font-bold text-slate-200">Celery Worker</div>
          <div className="text-[9px] text-emerald-400 uppercase font-bold">HEALTHY</div>
        </div>

        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 space-y-1">
          <ShieldCheck className="h-5 w-5 mx-auto text-emerald-400" />
          <div className="font-bold text-slate-200">Plugin SDK</div>
          <div className="text-[9px] text-emerald-400 uppercase font-bold">HEALTHY</div>
        </div>

        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 space-y-1">
          <Activity className="h-5 w-5 mx-auto text-emerald-400" />
          <div className="font-bold text-slate-200">DAG Workflows</div>
          <div className="text-[9px] text-emerald-400 uppercase font-bold">HEALTHY</div>
        </div>
      </div>
    </div>
  );
};
