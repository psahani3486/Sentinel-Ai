"use client";

import React, { useState } from "react";
import { ForecastRun } from "@/types/forecasting";
import { RiskForecastCard } from "@/components/forecasting/RiskForecastCard";
import { TrendingUp, Activity, ShieldCheck, Filter, ArrowUpRight, LineChart } from "lucide-react";
import Link from "next/link";

export default function ForecastDashboardPage() {
  const [filterRisk, setFilterRisk] = useState<string>("all");

  const [forecastRuns, setForecastRuns] = useState<ForecastRun[]>([
    {
      id: "fc-101",
      forecast_type: "quality_score_trend",
      algorithm_name: "LinearRegression",
      forecast_horizon_days: 7,
      overall_risk_level: "high",
      summary: "Quality score trajectory is downward over 7-day horizon.",
      execution_time_ms: 12.4,
      status: "completed",
      created_at: "2026-07-26T14:30:00Z",
      results: [
        {
          id: "res-101",
          target_metric: "Quality Score Trend (0-100%)",
          predicted_value: 82.5,
          confidence_interval_lower: 78.0,
          confidence_interval_upper: 87.0,
          trend_direction: "downward",
          risk_level: "high",
          explanation: "Data quality score projected at 82.5% in 7 days.",
          preventive_actions: {
            actions: ["Deploy quality SLA gate on staging pipeline."],
          },
          created_at: "2026-07-26T14:30:00Z",
        },
      ],
    },
    {
      id: "fc-102",
      forecast_type: "pipeline_failure_probability",
      algorithm_name: "LinearRegression",
      forecast_horizon_days: 14,
      overall_risk_level: "critical",
      summary: "Pipeline failure probability is upward.",
      execution_time_ms: 10.1,
      status: "completed",
      created_at: "2026-07-26T13:00:00Z",
      results: [
        {
          id: "res-102",
          target_metric: "Pipeline Timeout Failure Probability",
          predicted_value: 0.78,
          confidence_interval_lower: 0.65,
          confidence_interval_upper: 0.91,
          trend_direction: "upward",
          risk_level: "critical",
          explanation: "Pipeline timeout risk estimated at 78.0%.",
          preventive_actions: {
            actions: ["Expand socket connection timeout limits."],
          },
          created_at: "2026-07-26T13:00:00Z",
        },
      ],
    },
    {
      id: "fc-103",
      forecast_type: "data_drift_trend",
      algorithm_name: "LinearRegression",
      forecast_horizon_days: 7,
      overall_risk_level: "low",
      summary: "Feature distribution drift is stable.",
      execution_time_ms: 8.5,
      status: "completed",
      created_at: "2026-07-26T12:00:00Z",
      results: [
        {
          id: "res-103",
          target_metric: "Feature Distribution PSI Drift Metric",
          predicted_value: 0.04,
          confidence_interval_lower: 0.02,
          confidence_interval_upper: 0.06,
          trend_direction: "stable",
          risk_level: "low",
          explanation: "PSI drift projected to stay within normal bounds.",
          created_at: "2026-07-26T12:00:00Z",
        },
      ],
    },
  ]);

  const filtered = forecastRuns.filter((r) => {
    if (filterRisk !== "all" && r.overall_risk_level !== filterRisk) return false;
    return true;
  });

  return (
    <div className="space-y-8 p-8">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              Predictive Observability & Risk Forecasting
            </h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-indigo-500/10 px-2.5 py-1 text-xs font-semibold text-indigo-400 border border-indigo-500/20">
              <LineChart className="h-3.5 w-3.5" /> OLS Linear Regression
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Statistical forecasting models projecting future quality score degradation, drift trends, and failure risk.
          </p>
        </div>
      </div>

      {/* Risk Alert Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <RiskForecastCard
          riskLevel="critical"
          summary="Critical Pipeline Failure Risk: Ingestion socket timeout probability predicted to reach 78% in 14 days."
        />
        <RiskForecastCard
          riskLevel="high"
          summary="High Quality Degradation Risk: Quality score projected to drop to 82.5% (SLA target: 85%)."
        />
      </div>

      {/* Filters & Log */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <h2 className="text-lg font-bold text-white">Predictive Forecast Log</h2>

        <div className="flex items-center gap-3">
          <Filter className="h-4 w-4 text-slate-400" />
          <select
            value={filterRisk}
            onChange={(e) => setFilterRisk(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none"
          >
            <option value="all">All Risk Levels</option>
            <option value="critical">Critical Risk</option>
            <option value="high">High Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="low">Low Risk</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-lg overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="border-b border-slate-800 bg-slate-950/60 uppercase font-bold text-slate-400">
            <tr>
              <th className="py-3.5 px-4">Forecast Task</th>
              <th className="py-3.5 px-4">Algorithm</th>
              <th className="py-3.5 px-4">Horizon</th>
              <th className="py-3.5 px-4">Overall Risk</th>
              <th className="py-3.5 px-4">Summary Narrative</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {filtered.map((run) => (
              <tr key={run.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3.5 px-4 font-mono font-bold text-indigo-400 uppercase">{run.forecast_type}</td>
                <td className="py-3.5 px-4 font-mono text-slate-400">{run.algorithm_name}</td>
                <td className="py-3.5 px-4 font-mono font-bold text-slate-300">{run.forecast_horizon_days} Days</td>
                <td className="py-3.5 px-4 uppercase font-bold text-xs">
                  <span className={run.overall_risk_level === "critical" ? "text-rose-400" : run.overall_risk_level === "high" ? "text-amber-400" : "text-emerald-400"}>
                    {run.overall_risk_level}
                  </span>
                </td>
                <td className="py-3.5 px-4 text-slate-300 max-w-sm truncate">{run.summary}</td>
                <td className="py-3.5 px-4 text-right">
                  <Link
                    href={`/forecast/${run.id}`}
                    className="rounded border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-[11px] font-semibold text-indigo-400 hover:bg-indigo-500/20 inline-block"
                  >
                    View Forecast <ArrowUpRight className="h-3 w-3 inline" />
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
