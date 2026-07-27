"use client";

import React from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, Zap, ShieldCheck } from "lucide-react";
import { ActionChecklist } from "@/components/recommendations/ActionChecklist";
import { EvidencePanel } from "@/components/recommendations/EvidencePanel";
import Link from "next/link";

export default function RecommendationDetailPage() {
  const params = useParams();
  const recId = params.id as string;

  return (
    <div className="space-y-8 p-8">
      {/* Navigation Header */}
      <div>
        <Link
          href="/recommendations"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:underline mb-2"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Recommendation Dashboard
        </Link>
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Remediation Action Plan & Strategy Report
          </h1>
          <span className="font-mono text-xs text-slate-500">• {recId}</span>
        </div>
      </div>

      {/* Top Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Rank Priority Score</p>
          <div className="text-3xl font-extrabold font-mono text-emerald-400">#91.8</div>
          <p className="text-xs text-slate-500">Top 1% prioritized item</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Estimated Business Impact</p>
          <div className="text-3xl font-extrabold font-mono text-indigo-400">HIGH</div>
          <p className="text-xs text-slate-500">Restores data pipeline SLA</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Estimated Deployment Effort</p>
          <div className="text-3xl font-extrabold font-mono text-emerald-400">LOW</div>
          <p className="text-xs text-slate-500">Quick win deployment</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Confidence Score</p>
          <div className="text-3xl font-extrabold font-mono text-white">94.0%</div>
          <p className="text-xs text-slate-500">Correlated evidence weight</p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <ActionChecklist
          steps={[
            "Verify database connection string and password secrets in vault.",
            "Increase pipeline execution timeout limit from 5 to 15 minutes.",
            "Trigger manual pipeline retry execution.",
          ]}
        />

        <EvidencePanel
          evidences={[
            {
              id: "ev-101",
              title: "Pipeline Execution Error Log",
              description: "Ingestion pipeline connection socket timed out during batch fetch.",
              weight: 0.9,
              created_at: "2026-07-26T13:00:00Z",
            },
          ]}
        />
      </div>
    </div>
  );
}
