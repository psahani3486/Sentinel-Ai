"use client";

import React from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, Clock, ShieldCheck, Layers, Cpu } from "lucide-react";
import { Trace, Span } from "@/types/telemetry";
import { SpanTimeline } from "@/components/telemetry/SpanTimeline";
import Link from "next/link";

export default function TelemetryTraceDetailPage() {
  const params = useParams();
  const traceId = params.id as string;

  const mockSpans: Span[] = [
    {
      id: "s-1",
      span_id: "sp-root-01",
      trace_id_str: traceId,
      name: "POST /api/v1/validations/evaluate",
      service_name: "sentinel-api",
      status: "ok",
      duration_ms: 42.5,
      start_time: "2026-07-27T08:00:00Z",
      end_time: "2026-07-27T08:00:00.0425Z",
    },
    {
      id: "s-2",
      span_id: "sp-child-db",
      trace_id_str: traceId,
      parent_span_id: "sp-root-01",
      name: "SQL Query: FETCH dataset_rules",
      service_name: "postgresql",
      status: "ok",
      duration_ms: 12.1,
      start_time: "2026-07-27T08:00:00.002Z",
      end_time: "2026-07-27T08:00:00.0141Z",
    },
    {
      id: "s-3",
      span_id: "sp-child-engine",
      trace_id_str: traceId,
      parent_span_id: "sp-root-01",
      name: "Validation Engine: Evaluate Rule Suite",
      service_name: "validation-engine",
      status: "ok",
      duration_ms: 22.4,
      start_time: "2026-07-27T08:00:00.015Z",
      end_time: "2026-07-27T08:00:00.0374Z",
    },
  ];

  const mockTrace: Trace = {
    id: "tr-db-1",
    trace_id: traceId,
    name: "POST /api/v1/validations/evaluate",
    service_name: "sentinel-api",
    duration_ms: 42.5,
    status: "ok",
    start_time: "2026-07-27T08:00:00Z",
    end_time: "2026-07-27T08:00:00.0425Z",
    spans: mockSpans,
  };

  return (
    <div className="space-y-8 p-8">
      {/* Navigation Header */}
      <div>
        <Link
          href="/telemetry"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:underline mb-2"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Telemetry & APM Dashboard
        </Link>
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Trace Context: {mockTrace.trace_id}
          </h1>
          <span className="font-mono text-xs text-slate-500">• {mockTrace.name}</span>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Duration</p>
          <div className="text-3xl font-extrabold font-mono text-emerald-400">{mockTrace.duration_ms.toFixed(1)} ms</div>
          <p className="text-xs text-slate-500">End-to-End Latency</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Trace Spans</p>
          <div className="text-3xl font-extrabold font-mono text-indigo-400">{mockSpans.length} Spans</div>
          <p className="text-xs text-slate-500">1 Parent, 2 Children</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Primary Service</p>
          <div className="text-xl font-extrabold font-mono text-slate-100">{mockTrace.service_name}</div>
          <p className="text-xs text-slate-500">FastAPI Gateway</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Execution Status</p>
          <div className="text-xl font-extrabold font-mono text-emerald-400 uppercase">{mockTrace.status}</div>
          <p className="text-xs text-slate-500">Clean Exit Code</p>
        </div>
      </div>

      {/* Waterfall Span Timeline */}
      <SpanTimeline spans={mockSpans} totalDurationMs={mockTrace.duration_ms} />
    </div>
  );
}
