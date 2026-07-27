"use client";

import React, { useState } from "react";
import { Alert } from "@/types/alert";
import { Bell, ShieldAlert, CheckCircle2, AlertOctagon, Filter, Eye, Check } from "lucide-react";
import Link from "next/link";

export default function AlertCenterPage() {
  const [filterSeverity, setFilterSeverity] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  const [alerts, setAlerts] = useState<Alert[]>([
    {
      id: "alt-1",
      fingerprint: "fp-101",
      alert_type: "quality_score_drop",
      status: "open",
      severity: "critical",
      title: "Data Quality Score Drop (68.5%)",
      description: "Quality score 68.5% dropped below SLA target threshold 85.0%.",
      occurrence_count: 5,
      first_seen_at: "2026-07-26T14:00:00Z",
      last_seen_at: "2026-07-26T14:15:00Z",
      occurrences: [],
    },
    {
      id: "alt-2",
      fingerprint: "fp-102",
      alert_type: "validation_failure",
      status: "acknowledged",
      severity: "high",
      title: "Data Validation Suite Failure",
      description: "Validation run suite 'vr-902' failed execution rules.",
      occurrence_count: 2,
      first_seen_at: "2026-07-26T13:00:00Z",
      last_seen_at: "2026-07-26T13:30:00Z",
      occurrences: [],
    },
    {
      id: "alt-3",
      fingerprint: "fp-103",
      alert_type: "data_drift",
      status: "open",
      severity: "medium",
      title: "Feature Data Drift Detected (MEDIUM)",
      description: "Dataset overall drift index reached 28.5% (MEDIUM threshold).",
      occurrence_count: 1,
      first_seen_at: "2026-07-26T12:00:00Z",
      last_seen_at: "2026-07-26T12:00:00Z",
      occurrences: [],
    },
  ]);

  const handleAcknowledge = (id: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: "acknowledged" as const } : a))
    );
  };

  const handleResolve = (id: string) => {
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status: "resolved" as const } : a))
    );
  };

  const filtered = alerts.filter((a) => {
    if (filterSeverity !== "all" && a.severity !== filterSeverity) return false;
    if (filterStatus !== "all" && a.status !== filterStatus) return false;
    return true;
  });

  return (
    <div className="space-y-8 p-8">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              Enterprise Alert Center & Incident Operations
            </h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-rose-500/10 px-2.5 py-1 text-xs font-semibold text-rose-400 border border-rose-500/20">
              <Bell className="h-3.5 w-3.5" /> 2 Open Incidents
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Real-time incident response dashboard with fingerprint deduplication and severity escalation policies.
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-4 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <Filter className="h-4 w-4 text-slate-400" />
          <span className="text-xs font-bold text-slate-300 uppercase">Filters:</span>

          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none"
          >
            <option value="all">All Statuses</option>
            <option value="open">Open</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>
      </div>

      {/* Alerts Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-lg overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="border-b border-slate-800 bg-slate-950/60 uppercase font-bold text-slate-400">
            <tr>
              <th className="py-3.5 px-4">Severity</th>
              <th className="py-3.5 px-4">Title & Description</th>
              <th className="py-3.5 px-4">Alert Type</th>
              <th className="py-3.5 px-4 text-center">Occurrences</th>
              <th className="py-3.5 px-4">Status</th>
              <th className="py-3.5 px-4">Last Seen</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {filtered.map((alt) => (
              <tr key={alt.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3.5 px-4">
                  <span className="inline-flex items-center gap-1 rounded bg-rose-500/10 border border-rose-500/20 px-2.5 py-1 text-[10px] font-bold uppercase text-rose-400">
                    <AlertOctagon className="h-3 w-3" /> {alt.severity}
                  </span>
                </td>
                <td className="py-3.5 px-4 max-w-sm space-y-0.5">
                  <h4 className="font-semibold text-slate-100">{alt.title}</h4>
                  <p className="text-[11px] text-slate-400 truncate">{alt.description}</p>
                </td>
                <td className="py-3.5 px-4 font-mono text-[11px] text-slate-300">{alt.alert_type.toUpperCase()}</td>
                <td className="py-3.5 px-4 text-center font-mono font-bold text-indigo-400">{alt.occurrence_count}x</td>
                <td className="py-3.5 px-4">
                  <span className="rounded bg-slate-800 border border-slate-700 px-2 py-0.5 text-[10px] font-bold uppercase text-slate-300">
                    {alt.status}
                  </span>
                </td>
                <td className="py-3.5 px-4 font-mono text-slate-400">{new Date(alt.last_seen_at).toLocaleTimeString()}</td>
                <td className="py-3.5 px-4 text-right space-x-2">
                  {alt.status === "open" && (
                    <button
                      onClick={() => handleAcknowledge(alt.id)}
                      className="rounded border border-indigo-500/30 bg-indigo-500/10 px-2.5 py-1 text-[11px] font-semibold text-indigo-400 hover:bg-indigo-500/20"
                    >
                      <Eye className="h-3 w-3 inline mr-1" /> Ack
                    </button>
                  )}
                  {alt.status !== "resolved" && (
                    <button
                      onClick={() => handleResolve(alt.id)}
                      className="rounded border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-semibold text-emerald-400 hover:bg-emerald-500/20"
                    >
                      <Check className="h-3 w-3 inline mr-1" /> Resolve
                    </button>
                  )}
                  <Link
                    href={`/alerts/${alt.id}`}
                    className="rounded border border-slate-700 bg-slate-800 px-2.5 py-1 text-[11px] font-semibold text-slate-300 hover:bg-slate-700 inline-block"
                  >
                    Detail
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
