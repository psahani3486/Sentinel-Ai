"use client";

import React from "react";
import { AlertOctagon, AlertTriangle, ShieldCheck, Info } from "lucide-react";

interface RiskForecastCardProps {
  riskLevel: "critical" | "high" | "medium" | "low" | "info";
  summary: string;
}

export const RiskForecastCard: React.FC<RiskForecastCardProps> = ({ riskLevel, summary }) => {
  const getBadgeStyle = () => {
    switch (riskLevel) {
      case "critical":
        return { color: "text-rose-400 border-rose-500/30 bg-rose-500/10", icon: AlertOctagon };
      case "high":
        return { color: "text-amber-400 border-amber-500/30 bg-amber-500/10", icon: AlertTriangle };
      case "medium":
        return { color: "text-indigo-400 border-indigo-500/30 bg-indigo-500/10", icon: Info };
      default:
        return { color: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10", icon: ShieldCheck };
    }
  };

  const style = getBadgeStyle();
  const IconComp = style.icon;

  return (
    <div className={`rounded-xl border p-6 backdrop-blur-md shadow-lg space-y-3 ${style.color}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">
          <IconComp className="h-4 w-4" /> Operational Risk Forecast: {riskLevel}
        </span>
      </div>

      <p className="text-xs text-slate-200 leading-relaxed font-medium">{summary}</p>
    </div>
  );
};
