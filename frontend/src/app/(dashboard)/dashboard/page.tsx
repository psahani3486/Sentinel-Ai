"use client";

import React, { useState } from "react";
import { Database, ShieldCheck, AlertOctagon, Cpu, ArrowUpRight, Activity, Radio } from "lucide-react";
import { StatsCard } from "@/components/dashboard/StatsCard";
import { QualityScoreGauge } from "@/components/dashboard/QualityScoreGauge";
import { QualityTrendChart } from "@/components/dashboard/QualityTrendChart";
import { SeverityDistributionChart } from "@/components/dashboard/SeverityDistributionChart";
import { JobProgressBar } from "@/components/dashboard/JobProgressBar";
import { useJobWebSocket } from "@/hooks/useJobWebSocket";
import Link from "next/link";

export default function DashboardPage() {
  const { lastEvent, isConnected } = useJobWebSocket();

  const [stats] = useState({
    totalDatasets: 12,
    overallQualityScore: 94.8,
    activeAnomalies: 3,
    activeConnectors: 4,
  });

  const [trendData] = useState([
    { timestamp: "08:00", overall_score: 98.2 },
    { timestamp: "10:00", overall_score: 96.5 },
    { timestamp: "12:00", overall_score: 91.0 },
    { timestamp: "14:00", overall_score: 94.8 },
    { timestamp: "16:00", overall_score: 95.4 },
  ]);

  const [severityData] = useState([
    { name: "CRITICAL", value: 1 },
    { name: "HIGH", value: 2 },
    { name: "MEDIUM", value: 5 },
    { name: "LOW", value: 12 },
  ]);

  return (
    <div className="space-y-8 p-8">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              Industrial Observability Overview
            </h1>
            <span
              className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold border ${
                isConnected
                  ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                  : "bg-amber-500/10 text-amber-400 border-amber-500/20"
              }`}
            >
              <Radio className="h-3.5 w-3.5 animate-pulse" /> {isConnected ? "Live Telemetry Connected" : "Connecting WS..."}
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Real-time pipeline data quality, schema drift telemetry, and automated SLA validation.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            href="/datasets/upload"
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/20 hover:bg-indigo-500 transition-all"
          >
            <Database className="h-4 w-4" /> Ingest Dataset
          </Link>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Monitored Datasets"
          value={stats.totalDatasets}
          change="2 new"
          isPositive={true}
          icon={Database}
          color="text-indigo-400"
        />
        <StatsCard
          title="Data Quality Score"
          value={`${stats.overallQualityScore}%`}
          change="1.4%"
          isPositive={true}
          icon={ShieldCheck}
          color="text-emerald-400"
        />
        <StatsCard
          title="Active Anomalies"
          value={stats.activeAnomalies}
          change="1 critical"
          isPositive={false}
          icon={AlertOctagon}
          color="text-rose-400"
        />
        <StatsCard
          title="Telemetry Connectors"
          value={stats.activeConnectors}
          subtitle="IoT Sensors & PostgreSQL"
          icon={Cpu}
          color="text-sky-400"
        />
      </div>

      {/* Live Job Telemetry Banner (If active job event exists) */}
      {lastEvent && (
        <div className="space-y-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400">
            Active Real-Time Job Progress Stream
          </h3>
          <JobProgressBar
            jobId={lastEvent.job_id}
            jobType={lastEvent.job_type}
            status={lastEvent.status}
            progressPercentage={lastEvent.progress_percentage}
            message={lastEvent.latest_message}
            executionTimeMs={lastEvent.execution_time_ms}
          />
        </div>
      )}

      {/* Main Charts & Gauge Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Quality Score Gauge Card */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg flex flex-col items-center justify-center">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-6">
            System Data Health SLA
          </h3>
          <QualityScoreGauge score={stats.overallQualityScore} size={200} strokeWidth={16} />
          <p className="mt-6 text-center text-xs text-slate-400 max-w-xs">
            Weighted across completeness, accuracy, consistency, freshness, schema stability, and statistical bounds.
          </p>
        </div>

        {/* Quality Score Trend Chart */}
        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
                Data Quality Telemetry Trend
              </h3>
              <p className="text-xs text-slate-500">Historical quality score evaluations across runs</p>
            </div>
            <span className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-400">
              <Activity className="h-3.5 w-3.5" /> Real-time
            </span>
          </div>
          <QualityTrendChart data={trendData} />
        </div>
      </div>

      {/* Severity Breakdown & Recent Activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 mb-4">
            Rule Failure Severity Breakdown
          </h3>
          <SeverityDistributionChart data={severityData} />
        </div>

        <div className="lg:col-span-2 rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
              Recent Industrial Validation Executions
            </h3>
            <Link href="/validations" className="text-xs font-semibold text-indigo-400 hover:underline flex items-center gap-1">
              View All Runs <ArrowUpRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            {[
              { id: "run-101", dataset: "AI4I 2020 Predictive Maintenance", score: 99.5, status: "passed", time: "10 mins ago" },
              { id: "run-102", dataset: "NASA Turbofan Engine Degradation", score: 86.4, status: "failed", time: "42 mins ago" },
              { id: "run-103", dataset: "SECOM Semiconductor Telemetry", score: 92.0, status: "warning", time: "2 hours ago" },
            ].map((run) => (
              <div
                key={run.id}
                className="flex items-center justify-between rounded-lg border border-slate-800/80 bg-slate-950/60 p-4 transition-colors hover:border-slate-700"
              >
                <div>
                  <h4 className="text-sm font-semibold text-slate-200">{run.dataset}</h4>
                  <p className="text-xs text-slate-500">Execution ID: {run.id} • {run.time}</p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <span className="block text-sm font-bold text-slate-200">{run.score}%</span>
                    <span className="text-[10px] uppercase text-slate-500 font-semibold">Quality Score</span>
                  </div>
                  <Link
                    href={`/validations/${run.id}`}
                    className="rounded border border-slate-700 bg-slate-800 px-3 py-1 text-xs font-medium text-slate-300 hover:bg-slate-700"
                  >
                    Details
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
