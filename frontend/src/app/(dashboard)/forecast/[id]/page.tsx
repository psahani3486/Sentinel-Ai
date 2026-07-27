"use client";

import React from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, LineChart, ShieldCheck } from "lucide-react";
import { TrendChart } from "@/components/forecasting/TrendChart";
import { ForecastTimeline } from "@/components/forecasting/ForecastTimeline";
import Link from "next/link";

export default function ForecastDetailPage() {
  const params = useParams();
  const runId = params.id as string;

  return (
    <div className="space-y-8 p-8">
      {/* Navigation Header */}
      <div>
        <Link
          href="/forecast"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:underline mb-2"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Forecast Dashboard
        </Link>
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Predictive Risk Forecast Report
          </h1>
          <span className="font-mono text-xs text-slate-500">• {runId}</span>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Statistical Algorithm</p>
          <div className="text-2xl font-extrabold font-mono text-indigo-400">Linear Regression</div>
          <p className="text-xs text-slate-500">Ordinary Least Squares</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Forecast Horizon</p>
          <div className="text-3xl font-extrabold font-mono text-white">7 Days</div>
          <p className="text-xs text-slate-500">Ahead projection</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Predicted Value</p>
          <div className="text-3xl font-extrabold font-mono text-emerald-400">82.50%</div>
          <p className="text-xs text-slate-500">Quality score target</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Operational Risk Level</p>
          <div className="text-3xl font-extrabold font-mono text-amber-400">HIGH</div>
          <p className="text-xs text-slate-500">SLA breach risk</p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <TrendChart
          predictedValue={82.5}
          lowerBound={78.0}
          upperBound={87.0}
          trendDirection="downward"
        />

        <ForecastTimeline
          predictedValue={82.5}
          horizonDays={7}
        />
      </div>
    </div>
  );
}
