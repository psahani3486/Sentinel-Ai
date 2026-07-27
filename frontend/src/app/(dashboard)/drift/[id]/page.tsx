"use client";

import React from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, Database, Clock } from "lucide-react";
import { DriftScoreCard } from "@/components/drift/DriftScoreCard";
import { ColumnDriftTable } from "@/components/drift/ColumnDriftTable";
import { DistributionComparisonChart } from "@/components/drift/DistributionComparisonChart";
import Link from "next/link";

export default function DriftDetailPage() {
  const params = useParams();
  const runId = params.id as string;

  return (
    <div className="space-y-8 p-8">
      {/* Navigation & Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link
            href="/drift"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:underline mb-2"
          >
            <ArrowLeft className="h-3.5 w-3.5" /> Back to Drift Observatory
          </Link>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              Data Drift Audit Report
            </h1>
            <span className="font-mono text-xs text-slate-500">• {runId}</span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Comparative feature analysis comparing current dataset version against baseline reference.
          </p>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono text-slate-400 border border-slate-800 bg-slate-900/60 p-3 rounded-lg">
          <span className="flex items-center gap-1.5"><Database className="h-4 w-4 text-indigo-400" /> AI4I 2020 Dataset</span>
          <span className="flex items-center gap-1.5"><Clock className="h-4 w-4 text-emerald-400" /> 14.8 ms Execution</span>
        </div>
      </div>

      {/* Score Card */}
      <DriftScoreCard
        score={28.5}
        status="medium"
        driftedColumnsCount={3}
        totalColumnsAnalyzed={7}
      />

      {/* Distribution Chart */}
      <DistributionComparisonChart />

      {/* Column Table */}
      <ColumnDriftTable
        results={[
          {
            id: "r1",
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
            id: "r2",
            column_name: "process_temperature",
            column_type: "numeric",
            detector_type: "mean_drift",
            drift_detected: true,
            drift_score: 0.185,
            threshold: 0.15,
            severity: "medium",
            explanation: "Mean shifted by 0.19 std dev (Base: 308.2, Curr: 312.4)",
          },
        ]}
      />
    </div>
  );
}
