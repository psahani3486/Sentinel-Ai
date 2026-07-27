"use client";

import React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, ShieldCheck, CheckCircle2, AlertTriangle, XCircle, Clock } from "lucide-react";
import { ValidationRuleTable } from "@/components/validation/ValidationRuleTable";
import type { RuleResultItem } from "@/types/validation";

export default function ValidationDetailsPage() {
  const params = useParams();
  const validationId = params.id as string;

  const sampleResults: RuleResultItem[] = [
    { id: "r1", rule_type: "missing_values", status: "passed", severity: "high", message: "Missing values percentage is within SLA limit (0.0%).", execution_time_ms: 2.1, score_impact: 0 },
    { id: "r2", rule_type: "null_column", status: "passed", severity: "high", message: "No completely null columns detected in dataset schema.", execution_time_ms: 1.5, score_impact: 0 },
    { id: "r3", rule_type: "data_completeness", status: "passed", severity: "critical", message: "Dataset completeness SLA satisfied (100.0% >= 95.0%).", execution_time_ms: 1.2, score_impact: 0 },
    { id: "r4", rule_type: "duplicate_rows", status: "passed", severity: "medium", message: "Zero duplicate rows detected.", execution_time_ms: 3.4, score_impact: 0 },
    { id: "r5", rule_type: "outlier", status: "warning", severity: "medium", message: "Statistical outliers detected in Rotational speed [rpm] channel.", affected_columns: ["Rotational speed [rpm]"], execution_time_ms: 4.5, score_impact: 5 },
    { id: "r6", rule_type: "constant_columns", status: "warning", severity: "medium", message: "Constant single-value columns found in dataset.", affected_columns: ["sensor_flatline_dummy"], execution_time_ms: 1.1, score_impact: 5 },
  ];

  return (
    <div className="space-y-6 p-8">
      {/* Back Link */}
      <Link href="/validations" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-slate-200">
        <ArrowLeft className="h-4 w-4" /> Back to Validation Runs Audit Log
      </Link>

      {/* Execution Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between rounded-xl border border-slate-800 bg-slate-900/80 p-6 backdrop-blur-md shadow-lg">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-extrabold text-white">Validation Run Audit</h1>
            <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
              <CheckCircle2 className="h-3.5 w-3.5" /> COMPLETED
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-400 font-mono">Run ID: {validationId} • Target Asset: AI4I 2020 Predictive Maintenance</p>
        </div>

        <div className="text-right">
          <span className="block text-3xl font-extrabold text-emerald-400">99.5%</span>
          <span className="text-xs uppercase font-bold text-slate-500 tracking-wider">Overall Quality Score</span>
        </div>
      </div>

      {/* Category Scores Overview */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <span className="text-xs text-slate-500 uppercase font-semibold">Completeness</span>
          <p className="mt-1 text-lg font-bold text-emerald-400">100.0%</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <span className="text-xs text-slate-500 uppercase font-semibold">Consistency</span>
          <p className="mt-1 text-lg font-bold text-emerald-400">100.0%</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <span className="text-xs text-slate-500 uppercase font-semibold">Accuracy</span>
          <p className="mt-1 text-lg font-bold text-emerald-400">98.0%</p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
          <span className="text-xs text-slate-500 uppercase font-semibold">Freshness</span>
          <p className="mt-1 text-lg font-bold text-emerald-400">100.0%</p>
        </div>
      </div>

      {/* Detailed Rule Results */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold uppercase text-slate-300">Validation Rule Suite Results (22 Rules Evaluated)</h3>
        <ValidationRuleTable results={sampleResults} />
      </div>
    </div>
  );
}
