"use client";

import React, { useState } from "react";
import { RootCauseAnalysis } from "@/types/ai";
import { Cpu, ShieldCheck, Sparkles, AlertOctagon, ArrowUpRight, Play } from "lucide-react";
import Link from "next/link";

export default function RootCauseDashboardPage() {
  const [analyses, setAnalyses] = useState<RootCauseAnalysis[]>([
    {
      id: "rca-101",
      analysis_type: "validation_failure",
      target_entity_type: "validation_run",
      target_entity_id: "vr-902",
      summary: "Validation suite failed with 3 rule violations across columns ['air_temperature', 'rotational_speed'].",
      probable_root_cause: "High failure rate in rule categories ['invalid_numeric_values', 'outliers'] impacting column integrity.",
      confidence_score: 95.0,
      severity: "critical",
      affected_components: { components: ["air_temperature", "rotational_speed"] },
      recommended_actions: {
        actions: [
          "Inspect raw input data for unexpected nulls or invalid data types.",
          "Verify upstream ETL transformation steps for broken string-to-numeric casting.",
        ],
      },
      status: "completed",
      execution_time_ms: 12.4,
      llm_provider_name: "MockLLMProvider",
      created_at: "2026-07-26T14:15:00Z",
      evidences: [],
    },
    {
      id: "rca-102",
      analysis_type: "data_drift",
      target_entity_type: "drift_run",
      target_entity_id: "dr-401",
      summary: "Significant population drift detected on columns ['torque', 'tool_wear'] (Peak PSI: 0.285).",
      probable_root_cause: "Statistical distribution shift resulting from upstream population changes.",
      confidence_score: 88.5,
      severity: "high",
      affected_components: { components: ["torque", "tool_wear"] },
      recommended_actions: {
        actions: [
          "Compare current feature histograms against baseline reference distributions.",
          "Check for recent changes in upstream data collection hardware.",
        ],
      },
      status: "completed",
      execution_time_ms: 8.2,
      llm_provider_name: "MockLLMProvider",
      created_at: "2026-07-26T12:00:00Z",
      evidences: [],
    },
  ]);

  return (
    <div className="space-y-8 p-8">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              AI Root Cause Analysis Engine
            </h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-indigo-500/10 px-2.5 py-1 text-xs font-semibold text-indigo-400 border border-indigo-500/20">
              <Sparkles className="h-3.5 w-3.5" /> Pluggable Hybrid Engine
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Enterprise Root Cause Analysis (RCA) explaining why validation failures, data drift events, and alerts occurred.
          </p>
        </div>
      </div>

      {/* Summary Score Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Total RCA Reports</p>
          <div className="text-3xl font-extrabold font-mono text-white">{analyses.length}</div>
          <p className="text-xs text-slate-500">Automated diagnostic runs</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Average Confidence Score</p>
          <div className="text-3xl font-extrabold font-mono text-emerald-400">91.8%</div>
          <p className="text-xs text-slate-500">Multi-source statistical certainty</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Active LLM Provider</p>
          <div className="text-3xl font-extrabold font-mono text-indigo-400">MockLLMProvider</div>
          <p className="text-xs text-slate-500">Pluggable hybrid provider (100% offline)</p>
        </div>
      </div>

      {/* Reports Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-lg overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="border-b border-slate-800 bg-slate-950/60 uppercase font-bold text-slate-400">
            <tr>
              <th className="py-3.5 px-4">Severity</th>
              <th className="py-3.5 px-4">Analysis Type</th>
              <th className="py-3.5 px-4">Summary & Probable Cause</th>
              <th className="py-3.5 px-4 text-center">Confidence</th>
              <th className="py-3.5 px-4">Timestamp</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {analyses.map((rca) => (
              <tr key={rca.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3.5 px-4">
                  <span className="inline-flex items-center gap-1 rounded bg-rose-500/10 border border-rose-500/20 px-2.5 py-1 text-[10px] font-bold uppercase text-rose-400">
                    <AlertOctagon className="h-3 w-3" /> {rca.severity}
                  </span>
                </td>
                <td className="py-3.5 px-4 font-mono font-bold text-indigo-400 uppercase">{rca.analysis_type}</td>
                <td className="py-3.5 px-4 max-w-md space-y-0.5">
                  <h4 className="font-semibold text-slate-100">{rca.summary}</h4>
                  <p className="text-[11px] text-slate-400 truncate">{rca.probable_root_cause}</p>
                </td>
                <td className="py-3.5 px-4 text-center font-mono font-bold text-emerald-400">{rca.confidence_score.toFixed(1)}%</td>
                <td className="py-3.5 px-4 font-mono text-slate-400">{new Date(rca.created_at).toLocaleTimeString()}</td>
                <td className="py-3.5 px-4 text-right">
                  <Link
                    href={`/analysis/${rca.id}`}
                    className="rounded border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-[11px] font-semibold text-indigo-400 hover:bg-indigo-500/20 inline-block"
                  >
                    Inspect RCA <ArrowUpRight className="h-3 w-3 inline" />
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
