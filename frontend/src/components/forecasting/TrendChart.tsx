"use client";

import React from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface TrendChartProps {
  predictedValue: number;
  lowerBound: number;
  upperBound: number;
  trendDirection: "upward" | "downward" | "stable";
}

export const TrendChart: React.FC<TrendChartProps> = ({
  predictedValue,
  lowerBound,
  upperBound,
  trendDirection,
}) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
            Metric Trajectory & 95% Confidence Bounds
          </h3>
          <p className="text-xs text-slate-500">Ordinary Least Squares Statistical Regression Projection</p>
        </div>
        <div className="flex items-center gap-1 font-mono text-xs font-bold uppercase px-2.5 py-1 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
          {trendDirection === "upward" && <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />}
          {trendDirection === "downward" && <TrendingDown className="h-3.5 w-3.5 text-rose-400" />}
          {trendDirection === "stable" && <Minus className="h-3.5 w-3.5 text-slate-400" />}
          <span>{trendDirection} Trend</span>
        </div>
      </div>

      {/* Visual Band Display */}
      <div className="rounded-lg border border-slate-800 bg-slate-950/80 p-5 space-y-4">
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400 font-medium">95% Lower Confidence Bound</span>
          <span className="font-mono font-bold text-slate-300">{lowerBound.toFixed(2)}</span>
        </div>

        <div className="relative h-4 w-full rounded-full bg-slate-800 overflow-hidden">
          <div className="absolute inset-y-0 bg-indigo-500/30 rounded-full left-[20%] right-[20%]" />
          <div className="absolute inset-y-0 bg-emerald-400 w-2 rounded-full left-[50%] -ml-1 shadow-md shadow-emerald-500/50" />
        </div>

        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-400 font-medium">95% Upper Confidence Bound</span>
          <span className="font-mono font-bold text-slate-300">{upperBound.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
};
