"use client";

import React from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, AlertOctagon, Check, Eye } from "lucide-react";
import { AlertTimeline } from "@/components/alerts/AlertTimeline";
import Link from "next/link";

export default function AlertDetailPage() {
  const params = useParams();
  const alertId = params.id as string;

  return (
    <div className="space-y-8 p-8">
      {/* Navigation Header */}
      <div className="flex items-center justify-between">
        <div>
          <Link
            href="/alerts"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:underline mb-2"
          >
            <ArrowLeft className="h-3.5 w-3.5" /> Back to Alert Center
          </Link>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              Incident Audit & Escalation Report
            </h1>
            <span className="font-mono text-xs text-slate-500">• {alertId}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button className="rounded-lg border border-indigo-500/30 bg-indigo-500/10 px-4 py-2 text-xs font-semibold text-indigo-400 hover:bg-indigo-500/20">
            <Eye className="h-3.5 w-3.5 inline mr-1.5" /> Acknowledge
          </button>
          <button className="rounded-lg bg-emerald-600 px-4 py-2 text-xs font-semibold text-white hover:bg-emerald-500">
            <Check className="h-3.5 w-3.5 inline mr-1.5" /> Resolve Incident
          </button>
        </div>
      </div>

      {/* Incident Overview Card */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
        <div className="flex items-center justify-between">
          <span className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold border uppercase bg-rose-500/10 text-rose-400 border-rose-500/20">
            <AlertOctagon className="h-4 w-4" /> CRITICAL INCIDENT
          </span>
          <span className="font-mono text-xs text-indigo-400 font-bold">5x Deduplicated Occurrences</span>
        </div>

        <h2 className="text-xl font-bold text-white">Data Quality Score Drop (68.5%)</h2>
        <p className="text-sm text-slate-400">
          Quality score 68.5% dropped below SLA target threshold 85.0%. Triggered by 3 critical rule failures during validation run.
        </p>

        <div className="grid grid-cols-2 gap-4 text-xs font-mono pt-4 border-t border-slate-800 text-slate-400">
          <div><span className="text-slate-500">Fingerprint:</span> fp-902-quality-drop-ai4i</div>
          <div><span className="text-slate-500">First Seen:</span> 2026-07-26 14:00:00 UTC</div>
        </div>
      </div>

      {/* Timeline */}
      <AlertTimeline
        occurrences={[
          {
            id: "occ-2",
            severity: "critical",
            message: "Escalated to CRITICAL after 5th consecutive quality score drop violation.",
            event_payload: { quality_score: 68.5, target_sla: 85.0, occurrences: 5 },
            created_at: "2026-07-26T14:15:00Z",
          },
          {
            id: "occ-1",
            severity: "high",
            message: "Initial quality score drop candidate detected.",
            event_payload: { quality_score: 72.0, target_sla: 85.0, occurrences: 1 },
            created_at: "2026-07-26T14:00:00Z",
          },
        ]}
      />
    </div>
  );
}
