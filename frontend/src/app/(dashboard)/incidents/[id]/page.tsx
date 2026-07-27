"use client";

import React from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, ShieldAlert, Brain, Zap, LineChart } from "lucide-react";
import { UnifiedTimeline } from "@/components/incidents/UnifiedTimeline";
import { EvidenceExplorer } from "@/components/incidents/EvidenceExplorer";
import { CorrelationGraph } from "@/components/incidents/CorrelationGraph";
import Link from "next/link";

export default function IncidentDetailPage() {
  const params = useParams();
  const incId = params.id as string;

  const mockEvents = [
    {
      id: "ev-101",
      timestamp: "2026-07-26T14:00:00Z",
      event_type: "validation_failed",
      severity: "high" as const,
      description: "Validation rule 'missing_values' failed on column 'sensor_temp': Found 12 null values.",
      evidence_link: "/validations/val-101",
      payload: { rule: "missing_values", column: "sensor_temp", failed_count: 12 },
      created_at: "2026-07-26T14:00:00Z",
    },
    {
      id: "ev-102",
      timestamp: "2026-07-26T14:05:00Z",
      event_type: "drift_detected",
      severity: "medium" as const,
      description: "Feature distribution drift detected on feature 'sensor_temp'. PSI: 0.18.",
      evidence_link: "/drift",
      payload: { feature: "sensor_temp", psi: 0.18 },
      created_at: "2026-07-26T14:05:00Z",
    },
    {
      id: "ev-103",
      timestamp: "2026-07-26T14:10:00Z",
      event_type: "alert_triggered",
      severity: "critical" as const,
      description: "Incident alert triggered: Quality Score Drop below 85% SLA.",
      evidence_link: "/alerts/alt-101",
      payload: { alert_type: "quality_score_drop", threshold: 85.0 },
      created_at: "2026-07-26T14:10:00Z",
    },
    {
      id: "ev-104",
      timestamp: "2026-07-26T14:15:00Z",
      event_type: "rca_completed",
      severity: "info" as const,
      description: "AI Root Cause Analysis completed: Probable root cause isolated to malformed pre-ingestion strings.",
      evidence_link: "/analysis/rca-101",
      payload: { confidence: 92.5, root_cause: "Malformed pre-ingestion strings" },
      created_at: "2026-07-26T14:15:00Z",
    },
    {
      id: "ev-105",
      timestamp: "2026-07-26T14:20:00Z",
      event_type: "recommendation_generated",
      severity: "info" as const,
      description: "Actionable remediation recommendation generated: Filter or cast unparseable strings.",
      evidence_link: "/recommendations/rec-101",
      payload: { priority_score: 91.8, impact: "HIGH", effort: "LOW" },
      created_at: "2026-07-26T14:20:00Z",
    },
  ];

  return (
    <div className="space-y-8 p-8">
      {/* Navigation Header */}
      <div>
        <Link
          href="/incidents"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:underline mb-2"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Incident Workspace Log
        </Link>
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Incident Investigation Workspace
          </h1>
          <span className="font-mono text-xs text-slate-500">• {incId}</span>
        </div>
      </div>

      {/* Top Incident Summary Card */}
      <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-6 backdrop-blur-md shadow-lg space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-2">
            <ShieldAlert className="h-4 w-4" /> Critical Data Quality SLA Breach
          </span>
          <span className="font-mono text-xs font-bold uppercase px-3 py-1 rounded bg-slate-900 text-indigo-400 border border-slate-800">
            Status: Investigating
          </span>
        </div>

        <p className="text-sm text-slate-200 leading-relaxed font-medium">
          Unified incident workspace correlating 5 platform signals across Validation Runs, Feature Drift, Alert Center, AI Root Cause Analysis, and Remediation Engine.
        </p>

        {/* AI Correlation Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 border-t border-rose-500/20">
          <div className="space-y-1">
            <span className="text-[11px] font-bold text-amber-400 uppercase flex items-center gap-1">
              <Brain className="h-3.5 w-3.5" /> AI Root Cause
            </span>
            <p className="text-xs text-slate-300">Malformed string values in pre-ingestion stream.</p>
          </div>

          <div className="space-y-1">
            <span className="text-[11px] font-bold text-emerald-400 uppercase flex items-center gap-1">
              <Zap className="h-3.5 w-3.5" /> Remediation Action
            </span>
            <p className="text-xs text-slate-300">Cast unparseable strings prior to SQL commit.</p>
          </div>

          <div className="space-y-1">
            <span className="text-[11px] font-bold text-indigo-400 uppercase flex items-center gap-1">
              <LineChart className="h-3.5 w-3.5" /> Risk Forecast
            </span>
            <p className="text-xs text-slate-300">Quality score projected to recover in 7 days.</p>
          </div>
        </div>
      </div>

      {/* Signal Correlation Graph */}
      <CorrelationGraph title="Telemetry Signal Correlation Graph" />

      {/* Unified Timeline & Evidence Explorer */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <UnifiedTimeline events={mockEvents} />
        <EvidenceExplorer events={mockEvents} />
      </div>
    </div>
  );
}
