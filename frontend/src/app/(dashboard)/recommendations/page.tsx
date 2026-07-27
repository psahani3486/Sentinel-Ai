"use client";

import React, { useState } from "react";
import { Recommendation } from "@/types/recommendation";
import { PriorityMatrix } from "@/components/recommendations/PriorityMatrix";
import { Zap, Target, ShieldCheck, ArrowUpRight, Filter, Sparkles } from "lucide-react";
import Link from "next/link";

export default function RecommendationDashboardPage() {
  const [filterPriority, setFilterPriority] = useState<string>("all");

  const [recommendations, setRecommendations] = useState<Recommendation[]>([
    {
      id: "rec-101",
      category: "validation_failure",
      priority: "high",
      title: "Remediate Data Validation Failures on ['air_temperature', 'rotational_speed']",
      description: "Enforce strict pre-ingestion type casting and sanitize malformed string representations.",
      estimated_impact: "HIGH",
      estimated_effort: "LOW",
      confidence_score: 92.0,
      priority_score: 87.9,
      suggested_next_steps: {
        steps: [
          "Filter or cast unparseable string values prior to SQL database insert.",
          "Update validation rule parameters to tolerate expected operational noise bounds.",
        ],
      },
      status: "active",
      execution_time_ms: 10.5,
      created_at: "2026-07-26T14:15:00Z",
      evidences: [],
    },
    {
      id: "rec-102",
      category: "pipeline_failure",
      priority: "critical",
      title: "Restore Pipeline Database Connection & Timeout Limits",
      description: "Verify database credentials, network connection strings, and socket timeout parameters.",
      estimated_impact: "HIGH",
      estimated_effort: "LOW",
      confidence_score: 94.0,
      priority_score: 91.8,
      suggested_next_steps: {
        steps: [
          "Verify database connection string and password secrets in vault.",
          "Increase pipeline execution timeout limit from 5 to 15 minutes.",
        ],
      },
      status: "active",
      execution_time_ms: 8.2,
      created_at: "2026-07-26T13:00:00Z",
      evidences: [],
    },
    {
      id: "rec-103",
      category: "data_drift",
      priority: "medium",
      title: "Re-Baseline Data Drift Reference Distributions",
      description: "Re-calibrate baseline feature quantiles if distribution shift reflects valid operational evolution.",
      estimated_impact: "MEDIUM",
      estimated_effort: "LOW",
      confidence_score: 88.0,
      priority_score: 70.6,
      suggested_next_steps: {
        steps: [
          "Inspect dual-histogram distribution overlay in Data Drift Observatory.",
          "Promote latest ingested dataset version to reference baseline.",
        ],
      },
      status: "active",
      execution_time_ms: 7.1,
      created_at: "2026-07-26T12:00:00Z",
      evidences: [],
    },
  ]);

  const filtered = recommendations.filter((r) => {
    if (filterPriority !== "all" && r.priority !== filterPriority) return false;
    return true;
  });

  return (
    <div className="space-y-8 p-8">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              AI Remediation Recommendation Engine
            </h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
              <Zap className="h-3.5 w-3.5" /> 2 Quick Wins Identified
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Prioritized remediation actions ranked by weighted Business Impact, Severity, Confidence, and Effort.
          </p>
        </div>
      </div>

      {/* Priority Matrix 2x2 */}
      <PriorityMatrix recommendations={recommendations} />

      {/* Filters & Ranked List */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <h2 className="text-lg font-bold text-white">Ranked Recommendation Backlog</h2>

        <div className="flex items-center gap-3">
          <Filter className="h-4 w-4 text-slate-400" />
          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none"
          >
            <option value="all">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
          </select>
        </div>
      </div>

      {/* Recommendation Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-lg overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="border-b border-slate-800 bg-slate-950/60 uppercase font-bold text-slate-400">
            <tr>
              <th className="py-3.5 px-4">Rank Score</th>
              <th className="py-3.5 px-4">Category</th>
              <th className="py-3.5 px-4">Title & Remediation Advice</th>
              <th className="py-3.5 px-4 text-center">Impact / Effort</th>
              <th className="py-3.5 px-4 text-center">Confidence</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {filtered.map((rec) => (
              <tr key={rec.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3.5 px-4 font-mono font-extrabold text-emerald-400 text-sm">
                  #{rec.priority_score.toFixed(1)}
                </td>
                <td className="py-3.5 px-4 font-mono font-bold text-indigo-400 uppercase">{rec.category}</td>
                <td className="py-3.5 px-4 max-w-md space-y-0.5">
                  <h4 className="font-semibold text-slate-100">{rec.title}</h4>
                  <p className="text-[11px] text-slate-400 truncate">{rec.description}</p>
                </td>
                <td className="py-3.5 px-4 text-center">
                  <span className="inline-flex gap-1.5 font-mono text-[10px] font-bold">
                    <span className="text-emerald-400">Imp: {rec.estimated_impact}</span>
                    <span className="text-slate-500">|</span>
                    <span className="text-indigo-400">Eff: {rec.estimated_effort}</span>
                  </span>
                </td>
                <td className="py-3.5 px-4 text-center font-mono font-bold text-slate-300">{rec.confidence_score.toFixed(1)}%</td>
                <td className="py-3.5 px-4 text-right">
                  <Link
                    href={`/recommendations/${rec.id}`}
                    className="rounded border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-[11px] font-semibold text-indigo-400 hover:bg-indigo-500/20 inline-block"
                  >
                    View Plan <ArrowUpRight className="h-3 w-3 inline" />
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
