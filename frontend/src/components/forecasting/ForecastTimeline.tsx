"use client";

import React from "react";
import { Calendar, ArrowRight } from "lucide-react";

interface ForecastTimelineProps {
  predictedValue: number;
  horizonDays: number;
}

export const ForecastTimeline: React.FC<ForecastTimelineProps> = ({ predictedValue, horizonDays }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          {horizonDays}-Day Horizon Telemetry Projection
        </h3>
        <p className="text-xs text-slate-500">Projected trend values along observation timeline</p>
      </div>

      <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950/60 p-4">
        <div className="flex items-center gap-3">
          <Calendar className="h-5 w-5 text-indigo-400" />
          <div>
            <div className="text-xs font-bold text-slate-200">Forecast Horizon</div>
            <div className="text-[11px] text-slate-500">{horizonDays} Days Ahead</div>
          </div>
        </div>

        <ArrowRight className="h-4 w-4 text-slate-500" />

        <div className="text-right">
          <div className="text-xs font-bold text-slate-400">Projected Value</div>
          <div className="font-mono text-base font-extrabold text-emerald-400">{predictedValue.toFixed(2)}</div>
        </div>
      </div>
    </div>
  );
};
