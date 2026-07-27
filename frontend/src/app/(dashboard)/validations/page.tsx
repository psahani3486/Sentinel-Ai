"use client";

import React, { useState } from "react";
import Link from "next/link";
import { ShieldCheck, CheckCircle2, AlertTriangle, XCircle, ArrowUpRight } from "lucide-react";
import type { ValidationRunItem } from "@/types/validation";

export default function ValidationsHistoryPage() {
  const [runs] = useState<ValidationRunItem[]>([
    {
      id: "run-ai4i-001",
      dataset_id: "ds-ai4i-2020",
      dataset_version_id: "ver-101",
      status: "passed",
      overall_score: 99.5,
      completeness_score: 100.0,
      consistency_score: 100.0,
      accuracy_score: 98.0,
      freshness_score: 100.0,
      execution_time_ms: 12.4,
      created_at: "2026-07-26T08:30:00Z",
    },
    {
      id: "run-nasa-002",
      dataset_id: "ds-nasa-turbofan",
      dataset_version_id: "ver-102",
      status: "failed",
      overall_score: 84.0,
      completeness_score: 90.0,
      consistency_score: 85.0,
      accuracy_score: 75.0,
      freshness_score: 95.0,
      execution_time_ms: 24.8,
      created_at: "2026-07-26T08:00:00Z",
    },
  ]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "passed":
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="h-3.5 w-3.5" /> PASSED
          </span>
        );
      case "failed":
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-500/10 px-2.5 py-1 text-xs font-semibold text-rose-400 border border-rose-500/20">
            <XCircle className="h-3.5 w-3.5" /> FAILED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/10 px-2.5 py-1 text-xs font-semibold text-amber-400 border border-amber-500/20">
            <AlertTriangle className="h-3.5 w-3.5" /> WARNING
          </span>
        );
    }
  };

  return (
    <div className="space-y-6 p-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white">
          Validation Run History & Audits
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Complete audit trail of validation engine runs, data quality scores, and historical trend evaluations.
        </p>
      </div>

      {/* Runs Table */}
      <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-xl">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-950/80 text-xs uppercase tracking-wider text-slate-400">
            <tr>
              <th className="px-6 py-4">Execution ID</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4">Quality Score</th>
              <th className="px-6 py-4">Execution Duration</th>
              <th className="px-6 py-4">Timestamp</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {runs.map((r) => (
              <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="px-6 py-4 font-mono font-semibold text-slate-100">{r.id}</td>
                <td className="px-6 py-4">{getStatusBadge(r.status)}</td>
                <td className="px-6 py-4 font-mono font-bold text-emerald-400">{r.overall_score}%</td>
                <td className="px-6 py-4 font-mono text-xs text-slate-400">{r.execution_time_ms} ms</td>
                <td className="px-6 py-4 text-xs text-slate-400">{new Date(r.created_at).toLocaleString()}</td>
                <td className="px-6 py-4 text-right">
                  <Link
                    href={`/validations/${r.id}`}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-400 hover:text-indigo-300"
                  >
                    View Details <ArrowUpRight className="h-3.5 w-3.5" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
