"use client";

import React, { useState } from "react";
import { GitCompare, ShieldAlert, ArrowUpRight } from "lucide-react";
import { DriftScoreCard } from "@/components/drift/DriftScoreCard";
import { ColumnDriftTable } from "@/components/drift/ColumnDriftTable";
import { DistributionComparisonChart } from "@/components/drift/DistributionComparisonChart";
import { DriftResult } from "@/types/drift";
import Link from "next/link";

export default function DriftDashboardPage() {
  const [mockScore] = useState(28.5);
  const [mockStatus] = useState("medium");

  const [mockResults] = useState<DriftResult[]>([
    {
      id: "dr-1",
      column_name: "air_temperature",
      column_type: "numeric",
      detector_type: "psi",
      drift_detected: true,
      drift_score: 0.2245,
      threshold: 0.1,
      severity: "high",
      explanation: "PSI score 0.2245 exceeds threshold 0.10 (Significant population shift)",
    },
    {
      id: "dr-2",
      column_name: "process_temperature",
      column_type: "numeric",
      detector_type: "mean_drift",
      drift_detected: true,
      drift_score: 0.185,
      threshold: 0.15,
      severity: "medium",
      explanation: "Mean shifted by 0.19 std dev (Base: 308.2, Curr: 312.4)",
    },
    {
      id: "dr-3",
      column_name: "rotational_speed",
      column_type: "numeric",
      detector_type: "jensen_shannon",
      drift_detected: false,
      drift_score: 0.042,
      threshold: 0.15,
      severity: "info",
      explanation: "Jensen-Shannon distance is 0.0420 within threshold 0.15",
    },
    {
      id: "dr-4",
      column_name: "torque_nm",
      column_type: "numeric",
      detector_type: "wasserstein",
      drift_detected: false,
      drift_score: 0.061,
      threshold: 0.10,
      severity: "info",
      explanation: "Wasserstein distance normalized is 0.0610 within threshold 0.10",
    },
    {
      id: "dr-5",
      column_name: "tool_wear_min",
      column_type: "numeric",
      detector_type: "numeric_distribution_drift",
      drift_detected: true,
      drift_score: 0.142,
      threshold: 0.10,
      severity: "medium",
      explanation: "Maximum CDF distribution distance (KS-statistic) is 0.1420",
    },
  ]);

  return (
    <div className="space-y-8 p-8">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              Data Drift & Feature Decay Observatory
            </h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-indigo-500/10 px-2.5 py-1 text-xs font-semibold text-indigo-400 border border-indigo-500/20">
              <GitCompare className="h-3.5 w-3.5" /> Baseline v1.0 vs Current v1.1
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Detect distribution shifts, statistical feature decay, and covariate drift using 10 specialized detectors.
          </p>
        </div>
      </div>

      {/* Score Card */}
      <DriftScoreCard
        score={mockScore}
        status={mockStatus}
        driftedColumnsCount={3}
        totalColumnsAnalyzed={7}
      />

      {/* Main Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <DistributionComparisonChart />
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
            Recent Drift Detection Runs
          </h3>

          <div className="space-y-3">
            {[
              { id: "run-d1", dataset: "AI4I 2020 Predictive Maintenance", score: 28.5, status: "medium", date: "Today, 14:20" },
              { id: "run-d2", dataset: "NASA Turbofan Engine Degradation", score: 64.0, status: "high", date: "Yesterday, 09:15" },
              { id: "run-d3", dataset: "SECOM Semiconductor Telemetry", score: 0.0, status: "no_drift", date: "2 days ago" },
            ].map((run) => (
              <div
                key={run.id}
                className="flex items-center justify-between rounded-lg border border-slate-800/80 bg-slate-950/60 p-4 transition-colors hover:border-slate-700"
              >
                <div>
                  <h4 className="text-sm font-semibold text-slate-200">{run.dataset}</h4>
                  <p className="text-xs text-slate-500">{run.date}</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <span className="block text-sm font-bold text-slate-200">{run.score}%</span>
                    <span className="text-[10px] uppercase text-slate-500 font-semibold">{run.status}</span>
                  </div>
                  <Link
                    href={`/drift/${run.id}`}
                    className="rounded border border-slate-700 bg-slate-800 p-1.5 text-slate-300 hover:bg-slate-700"
                  >
                    <ArrowUpRight className="h-4 w-4" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Column Table */}
      <ColumnDriftTable results={mockResults} />
    </div>
  );
}
