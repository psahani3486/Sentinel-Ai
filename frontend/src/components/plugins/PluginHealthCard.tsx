"use client";

import React from "react";
import { Plugin } from "@/types/plugin";
import { Activity, CheckCircle2, ShieldAlert, Cpu } from "lucide-react";

interface PluginHealthCardProps {
  plugin: Plugin;
}

export const PluginHealthCard: React.FC<PluginHealthCardProps> = ({ plugin }) => {
  const isEnabled = plugin.status === "enabled";

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <Activity className="h-4 w-4 text-indigo-400" /> Plugin Health & Metrics
        </h3>
        <span className={`text-xs font-mono font-bold uppercase px-2.5 py-1 rounded border ${
          isEnabled ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" : "bg-slate-800 text-slate-400 border-slate-700"
        }`}>
          {plugin.status}
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs font-mono">
        <div className="rounded border border-slate-800 bg-slate-950/60 p-3 space-y-1">
          <span className="text-[10px] text-slate-500 uppercase">Version</span>
          <div className="font-bold text-slate-200">{plugin.version}</div>
        </div>

        <div className="rounded border border-slate-800 bg-slate-950/60 p-3 space-y-1">
          <span className="text-[10px] text-slate-500 uppercase">Avg Latency</span>
          <div className="font-bold text-indigo-400">1.2ms</div>
        </div>

        <div className="rounded border border-slate-800 bg-slate-950/60 p-3 space-y-1">
          <span className="text-[10px] text-slate-500 uppercase">Min Platform Ver</span>
          <div className="font-bold text-slate-300">v{plugin.minimum_platform_version}</div>
        </div>

        <div className="rounded border border-slate-800 bg-slate-950/60 p-3 space-y-1">
          <span className="text-[10px] text-slate-500 uppercase">Memory Footprint</span>
          <div className="font-bold text-emerald-400">4.1 MB</div>
        </div>
      </div>
    </div>
  );
};
