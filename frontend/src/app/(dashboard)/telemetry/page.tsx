"use client";

import React, { useState } from "react";
import { MetricSnapshot, Trace } from "@/types/telemetry";
import { Activity, Gauge, Clock, ShieldCheck, ArrowUpRight, Cpu, Layers } from "lucide-react";
import { ServiceDependencyGraph } from "@/components/telemetry/ServiceDependencyGraph";
import Link from "next/link";

export default function TelemetryDashboardPage() {
  const [metrics, setMetrics] = useState<MetricSnapshot[]>([
    { id: "m-1", metric_name: "api_latency", metric_type: "latency", value: 12.4, unit: "ms", created_at: "2026-07-27T08:00:00Z" },
    { id: "m-2", metric_name: "api_throughput", metric_type: "throughput", value: 245.0, unit: "req/s", created_at: "2026-07-27T08:00:00Z" },
    { id: "m-3", metric_name: "request_count", metric_type: "request_count", value: 1420.0, unit: "requests", created_at: "2026-07-27T08:00:00Z" },
    { id: "m-4", metric_name: "worker_utilization", metric_type: "worker_utilization", value: 18.5, unit: "%", created_at: "2026-07-27T08:00:00Z" },
    { id: "m-5", metric_name: "workflow_duration", metric_type: "duration", value: 48.5, unit: "ms", created_at: "2026-07-27T08:00:00Z" },
  ]);

  const [traces, setTraces] = useState<Trace[]>([
    {
      id: "tr-db-1",
      trace_id: "tr-e89a2b1c",
      name: "POST /api/v1/validations/evaluate",
      service_name: "sentinel-api",
      duration_ms: 42.5,
      status: "ok",
      start_time: "2026-07-27T08:00:00Z",
      end_time: "2026-07-27T08:00:00.042Z",
      spans: [],
    },
  ]);

  return (
    <div className="space-y-8 p-8">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              Platform Telemetry, Metrics & Distributed Tracing
            </h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
              <Activity className="h-3.5 w-3.5" /> 6/6 Subsystems Healthy
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Internal observability monitoring platform throughput, API latency, worker utilization, queue depth, and APM distributed trace waterfalls.
          </p>
        </div>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">API Throughput</p>
          <div className="text-3xl font-extrabold font-mono text-emerald-400">245 req/s</div>
          <p className="text-xs text-slate-500">Live Traffic Rate</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">P99 API Latency</p>
          <div className="text-3xl font-extrabold font-mono text-indigo-400">12.4 ms</div>
          <p className="text-xs text-slate-500">Validation Evaluation</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Worker Utilization</p>
          <div className="text-3xl font-extrabold font-mono text-white">18.5%</div>
          <p className="text-xs text-slate-500">Celery Distributed Queue</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Workflow Duration</p>
          <div className="text-3xl font-extrabold font-mono text-amber-400">48.5 ms</div>
          <p className="text-xs text-slate-500">E2E Investigation DAG</p>
        </div>
      </div>

      {/* Service Dependency Graph */}
      <ServiceDependencyGraph />

      {/* Metrics Catalog Grid */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          Collected Telemetry Metric Samples
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {metrics.map((m) => (
            <div key={m.id} className="rounded-lg border border-slate-800 bg-slate-950/80 p-4 font-mono text-xs space-y-1">
              <div className="text-slate-400 text-[10px] uppercase font-bold">{m.metric_type}</div>
              <div className="text-sm font-bold text-slate-100">{m.metric_name}</div>
              <div className="text-lg font-extrabold text-indigo-400">
                {m.value} {m.unit}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tracing Log */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-lg overflow-hidden space-y-2 p-6">
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
          APM Distributed Trace Explorer
        </h3>

        <table className="w-full text-left text-xs font-mono">
          <thead className="border-b border-slate-800 bg-slate-950/60 uppercase font-bold text-slate-400">
            <tr>
              <th className="py-3 px-4">Trace ID</th>
              <th className="py-3 px-4">Operation Name</th>
              <th className="py-3 px-4">Service</th>
              <th className="py-3 px-4">Duration</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {traces.map((t) => (
              <tr key={t.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3 px-4 font-bold text-indigo-400">{t.trace_id}</td>
                <td className="py-3 px-4 text-slate-200">{t.name}</td>
                <td className="py-3 px-4 text-slate-400">{t.service_name}</td>
                <td className="py-3 px-4 font-bold text-emerald-400">{t.duration_ms.toFixed(1)} ms</td>
                <td className="py-3 px-4 uppercase font-bold text-emerald-400">{t.status}</td>
                <td className="py-3 px-4 text-right">
                  <Link
                    href={`/telemetry/${t.trace_id}`}
                    className="rounded border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-[11px] font-semibold text-indigo-400 hover:bg-indigo-500/20 inline-block"
                  >
                    Inspect Spans <ArrowUpRight className="h-3 w-3 inline" />
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
