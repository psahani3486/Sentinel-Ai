"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface DistributionComparisonChartProps {
  data?: Array<{ bin: string; baseline: number; current: number }>;
}

export const DistributionComparisonChart: React.FC<DistributionComparisonChartProps> = ({
  data,
}) => {
  const chartData = data || [
    { bin: "15-20", baseline: 45, current: 20 },
    { bin: "20-25", baseline: 120, current: 85 },
    { bin: "25-30", baseline: 250, current: 340 },
    { bin: "30-35", baseline: 180, current: 290 },
    { bin: "35-40", baseline: 60, current: 110 },
  ];

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Feature Distribution Histogram Comparison
        </h3>
        <p className="text-xs text-slate-500">Baseline distribution (v1.0) vs Current distribution (v1.1)</p>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
            <XAxis dataKey="bin" stroke="#94a3b8" fontSize={11} />
            <YAxis stroke="#94a3b8" fontSize={11} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#0f172a",
                borderColor: "#334155",
                borderRadius: "8px",
                fontSize: "12px",
              }}
            />
            <Legend wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }} />
            <Bar dataKey="baseline" name="Baseline Version" fill="#6366f1" radius={[4, 4, 0, 0]} />
            <Bar dataKey="current" name="Current Version" fill="#10b981" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
