"use client";

import React, { useState } from "react";
import { Incident } from "@/types/incident";
import { ShieldAlert, AlertTriangle, Activity, Filter, ArrowUpRight, CheckCircle2 } from "lucide-react";
import Link from "next/link";

export default function IncidentDashboardPage() {
  const [filterSeverity, setFilterSeverity] = useState<string>("all");

  const [incidents, setIncidents] = useState<Incident[]>([
    {
      id: "inc-101",
      title: "Critical Telemetry Ingestion Connection Socket Timeout",
      severity: "critical",
      status: "investigating",
      summary: "Unified incident investigation for 'Critical Telemetry Ingestion Connection Socket Timeout'. Correlated 5 platform signals.",
      root_cause_summary: "Ingestion pipeline connection socket timed out during batch fetch.",
      recommendations_summary: "Verify database connection string and password secrets in vault.",
      forecast_summary: "Pipeline failure probability is upward.",
      created_at: "2026-07-26T14:40:00Z",
      timeline_events: [],
    },
    {
      id: "inc-102",
      title: "Data Quality SLA Breach on Industrial Sensor Stream",
      severity: "high",
      status: "open",
      summary: "Unified incident investigation for 'Data Quality SLA Breach on Industrial Sensor Stream'. Correlated 4 platform signals.",
      root_cause_summary: "Found 12 null values on sensor_temp column.",
      recommendations_summary: "Filter or cast unparseable string values prior to SQL insert.",
      forecast_summary: "Quality score projected at 82.5% in 7 days.",
      created_at: "2026-07-26T13:00:00Z",
      timeline_events: [],
    },
  ]);

  const filtered = incidents.filter((i) => {
    if (filterSeverity !== "all" && i.severity !== filterSeverity) return false;
    return true;
  });

  return (
    <div className="space-y-8 p-8">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              Unified Incident Investigation Workspace
            </h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-rose-500/10 px-2.5 py-1 text-xs font-semibold text-rose-400 border border-rose-500/20">
              <ShieldAlert className="h-3.5 w-3.5" /> 1 Active Critical Incident
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Automatically correlates Validation Failures, Quality Reports, Schema Changes, Data Drift, Alerts, RCA, Recommendations, and Forecasts into a single investigation workspace.
          </p>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Incidents</p>
          <div className="text-3xl font-extrabold font-mono text-white">2</div>
          <p className="text-xs text-slate-500">Correlated platform incidents</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Open & Investigating</p>
          <div className="text-3xl font-extrabold font-mono text-rose-400">2</div>
          <p className="text-xs text-slate-500">Active investigation required</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Correlated Signals</p>
          <div className="text-3xl font-extrabold font-mono text-indigo-400">9</div>
          <p className="text-xs text-slate-500">Validation, Drift, Alert & AI</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Mean Time To Resolution</p>
          <div className="text-3xl font-extrabold font-mono text-emerald-400">14m</div>
          <p className="text-xs text-slate-500">Automated RCA correlation</p>
        </div>
      </div>

      {/* Filters & Incident List */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <h2 className="text-lg font-bold text-white">Active Incident Workspaces</h2>

        <div className="flex items-center gap-3">
          <Filter className="h-4 w-4 text-slate-400" />
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-lg overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="border-b border-slate-800 bg-slate-950/60 uppercase font-bold text-slate-400">
            <tr>
              <th className="py-3.5 px-4">Severity</th>
              <th className="py-3.5 px-4">Incident Workspace Title</th>
              <th className="py-3.5 px-4">Status</th>
              <th className="py-3.5 px-4">AI Root Cause Isolation</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {filtered.map((inc) => (
              <tr key={inc.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3.5 px-4 uppercase font-bold text-xs">
                  <span className={inc.severity === "critical" ? "text-rose-400" : "text-amber-400"}>
                    {inc.severity}
                  </span>
                </td>
                <td className="py-3.5 px-4 font-semibold text-slate-100 max-w-sm">{inc.title}</td>
                <td className="py-3.5 px-4 uppercase font-mono font-bold text-indigo-400">{inc.status}</td>
                <td className="py-3.5 px-4 text-slate-300 max-w-md truncate">{inc.root_cause_summary || inc.summary}</td>
                <td className="py-3.5 px-4 text-right">
                  <Link
                    href={`/incidents/${inc.id}`}
                    className="rounded border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-[11px] font-semibold text-indigo-400 hover:bg-indigo-500/20 inline-block"
                  >
                    Open Workspace <ArrowUpRight className="h-3 w-3 inline" />
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
