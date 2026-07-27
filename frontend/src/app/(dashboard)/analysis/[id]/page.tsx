"use client";

import React from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, Sparkles, AlertOctagon } from "lucide-react";
import { ConfidenceScoreCard } from "@/components/ai/ConfidenceScoreCard";
import { EvidenceTimeline } from "@/components/ai/EvidenceTimeline";
import { RecommendedActionsPanel } from "@/components/ai/RecommendedActionsPanel";
import Link from "next/link";

export default function AnalysisDetailPage() {
  const params = useParams();
  const analysisId = params.id as string;

  return (
    <div className="space-y-8 p-8">
      {/* Navigation Header */}
      <div>
        <Link
          href="/analysis"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:underline mb-2"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Root Cause Dashboard
        </Link>
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            AI Root Cause Analysis Report
          </h1>
          <span className="font-mono text-xs text-slate-500">• {analysisId}</span>
        </div>
      </div>

      {/* Top Confidence Score & Severity Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2">
          <ConfidenceScoreCard
            score={95.0}
            providerName="MockLLMProvider"
            executionTimeMs={12.4}
          />
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-2 flex flex-col justify-between">
          <span className="text-xs font-bold uppercase text-slate-400">Analysis Severity</span>
          <div className="text-2xl font-extrabold uppercase text-rose-400 flex items-center gap-2">
            <AlertOctagon className="h-6 w-6" /> CRITICAL
          </div>
          <span className="text-xs text-slate-500">Target Entity: validation_run (vr-902)</span>
        </div>
      </div>

      {/* Cause Overview Card */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">Executive RCA Summary</h3>
          <p className="mt-1 text-sm font-medium text-slate-200">
            Validation suite failed with 3 rule violations across columns <code className="text-indigo-400 font-mono">air_temperature</code> and <code className="text-indigo-400 font-mono">rotational_speed</code>.
          </p>
        </div>

        <div className="pt-4 border-t border-slate-800 space-y-1">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Probable Root Cause</h4>
          <p className="text-sm font-semibold text-rose-300">
            High failure rate in rule categories <code className="font-mono">invalid_numeric_values</code> and <code className="font-mono">outliers</code> impacting column integrity.
          </p>
        </div>
      </div>

      {/* Evidence & Recommended Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <EvidenceTimeline
          evidences={[
            {
              id: "ev-1",
              evidence_type: "failed_rule",
              title: "Failed Rule: invalid_numeric_values",
              description: "Found 14 invalid string values in numeric column 'air_temperature'.",
              evidence_payload: { column: "air_temperature", invalid_count: 14 },
              weight: 0.95,
              created_at: "2026-07-26T14:15:00Z",
            },
            {
              id: "ev-2",
              evidence_type: "failed_rule",
              title: "Failed Rule: outliers",
              description: "Found 8 values exceeding 3 standard deviations in 'rotational_speed'.",
              evidence_payload: { column: "rotational_speed", outlier_count: 8 },
              weight: 0.85,
              created_at: "2026-07-26T14:15:00Z",
            },
          ]}
        />

        <RecommendedActionsPanel
          actions={[
            "Inspect raw input data for unexpected nulls or invalid string characters.",
            "Verify upstream ETL transformation steps for broken numeric casting logic.",
            "Re-run data validation suite after clean ingestion batch retry.",
          ]}
        />
      </div>
    </div>
  );
}
