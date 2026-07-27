"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  Database,
  Table,
  Layers,
  BarChart2,
  ShieldCheck,
  History,
  Play,
} from "lucide-react";
import { SchemaExplorer } from "@/components/dataset/SchemaExplorer";
import { DatasetPreviewGrid } from "@/components/dataset/DatasetPreviewGrid";
import { ValidationRuleTable } from "@/components/validation/ValidationRuleTable";

export default function DatasetDetailsPage() {
  const params = useParams();
  const datasetId = params.id as string;
  const [activeTab, setActiveTab] = useState<"overview" | "preview" | "schema" | "profile" | "validation" | "history">("overview");
  const [isValidating, setIsValidating] = useState(false);

  const sampleSchema = [
    { column_name: "UDI", data_type: "integer", is_nullable: false, is_primary_key: true },
    { column_name: "Product ID", data_type: "string", is_nullable: false, is_primary_key: false },
    { column_name: "Type", data_type: "string", is_nullable: false, is_primary_key: false },
    { column_name: "Air temperature [K]", data_type: "float", is_nullable: false, is_primary_key: false },
    { column_name: "Process temperature [K]", data_type: "float", is_nullable: false, is_primary_key: false },
    { column_name: "Rotational speed [rpm]", data_type: "integer", is_nullable: false, is_primary_key: false },
    { column_name: "Torque [Nm]", data_type: "float", is_nullable: false, is_primary_key: false },
    { column_name: "Tool wear [min]", data_type: "integer", is_nullable: false, is_primary_key: false },
    { column_name: "Machine failure", data_type: "integer", is_nullable: false, is_primary_key: false },
  ];

  const samplePreviewRows = [
    { UDI: 1, "Product ID": "M14860", Type: "M", "Air temperature [K]": 298.1, "Process temperature [K]": 308.6, "Rotational speed [rpm]": 1551, "Torque [Nm]": 42.8, "Tool wear [min]": 0, "Machine failure": 0 },
    { UDI: 2, "Product ID": "L47181", Type: "L", "Air temperature [K]": 298.2, "Process temperature [K]": 308.7, "Rotational speed [rpm]": 1408, "Torque [Nm]": 46.3, "Tool wear [min]": 3, "Machine failure": 0 },
    { UDI: 3, "Product ID": "L47182", Type: "L", "Air temperature [K]": 298.1, "Process temperature [K]": 308.5, "Rotational speed [rpm]": 1498, "Torque [Nm]": 49.4, "Tool wear [min]": 5, "Machine failure": 0 },
  ];

  const sampleValidationResults = [
    { id: "v1", rule_type: "missing_values", status: "passed" as const, severity: "high" as const, message: "Missing values percentage is within SLA limit (0.0%).", execution_time_ms: 2.1, score_impact: 0 },
    { id: "v2", rule_type: "outlier", status: "warning" as const, severity: "medium" as const, message: "Statistical outliers detected in Rotational speed [rpm] channel.", affected_columns: ["Rotational speed [rpm]"], execution_time_ms: 4.5, score_impact: 5 },
    { id: "v3", rule_type: "negative_sensor_value", status: "passed" as const, severity: "critical" as const, message: "All physical sensor telemetry channels contain valid positive measurements.", execution_time_ms: 1.8, score_impact: 0 },
  ];

  const handleRunValidation = () => {
    setIsValidating(true);
    setTimeout(() => {
      setIsValidating(false);
      setActiveTab("validation");
    }, 1500);
  };

  return (
    <div className="space-y-6 p-8">
      {/* Back Link */}
      <Link href="/datasets" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-slate-200">
        <ArrowLeft className="h-4 w-4" /> Back to Datasets Catalog
      </Link>

      {/* Dataset Header Card */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between rounded-xl border border-slate-800 bg-slate-900/80 p-6 backdrop-blur-md shadow-lg">
        <div className="flex items-start gap-4">
          <div className="rounded-xl bg-indigo-500/10 p-3 text-indigo-400 border border-indigo-500/20">
            <Database className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-white">AI4I 2020 Predictive Maintenance</h1>
            <p className="mt-1 text-xs text-slate-400">ID: {datasetId} • Industrial Sensor Telemetry Protocol</p>
          </div>
        </div>

        <button
          onClick={handleRunValidation}
          disabled={isValidating}
          className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-emerald-500/20 hover:bg-emerald-500 disabled:opacity-50 transition-all"
        >
          <Play className="h-4 w-4 fill-white" /> {isValidating ? "Validating Engine..." : "Execute Validation Suite"}
        </button>
      </div>

      {/* Detail Tabs */}
      <div className="flex border-b border-slate-800">
        {[
          { id: "overview", label: "Overview", icon: Layers },
          { id: "preview", label: "Dataset Preview", icon: Table },
          { id: "schema", label: "Schema Explorer", icon: Database },
          { id: "profile", label: "Statistical Profile", icon: BarChart2 },
          { id: "validation", label: "Validation Results", icon: ShieldCheck },
          { id: "history", label: "Validation History", icon: History },
        ].map((t) => {
          const Icon = t.icon;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              className={`flex items-center gap-2 border-b-2 py-3 px-5 text-sm font-semibold transition-all ${
                activeTab === t.id
                  ? "border-indigo-500 text-indigo-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <Icon className="h-4 w-4" /> {t.label}
            </button>
          );
        })}
      </div>

      {/* Tab Contents */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <div className="md:col-span-2 space-y-6">
            <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-3">
              <h3 className="text-sm font-bold uppercase text-slate-300">Dataset Asset Summary</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Industrial synthetic maintenance dataset featuring 10,000 telemetry records collected from smart manufacturing CNC milling machine tools. Includes ambient air temperature, process temperature, rotational speed, torque, tool wear, and failure indicators.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
                <span className="text-xs text-slate-500 uppercase font-semibold">Total Rows</span>
                <p className="mt-1 text-xl font-bold text-white">10,000</p>
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
                <span className="text-xs text-slate-500 uppercase font-semibold">Total Columns</span>
                <p className="mt-1 text-xl font-bold text-white">9</p>
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
                <span className="text-xs text-slate-500 uppercase font-semibold">Quality Score</span>
                <p className="mt-1 text-xl font-bold text-emerald-400">99.5%</p>
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
                <span className="text-xs text-slate-500 uppercase font-semibold">File Size</span>
                <p className="mt-1 text-xl font-bold text-white">528 KB</p>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
            <h3 className="text-sm font-bold uppercase text-slate-300">Active Connector Lineage</h3>
            <div className="space-y-3 text-xs text-slate-400">
              <div className="flex justify-between border-b border-slate-800/60 pb-2">
                <span>Protocol</span>
                <span className="font-mono text-indigo-300">industrial_sensor</span>
              </div>
              <div className="flex justify-between border-b border-slate-800/60 pb-2">
                <span>Storage Path</span>
                <span className="font-mono text-slate-200">/data/samples/ai4i2020.csv</span>
              </div>
              <div className="flex justify-between border-b border-slate-800/60 pb-2">
                <span>Active Version</span>
                <span className="font-mono text-slate-200">v1.0.0</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "preview" && <DatasetPreviewGrid rows={samplePreviewRows} />}

      {activeTab === "schema" && <SchemaExplorer columns={sampleSchema} />}

      {activeTab === "profile" && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <h3 className="text-sm font-bold uppercase text-slate-300">Automated Statistical Insights</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="rounded-lg bg-slate-950 p-4 border border-slate-800">
              <span className="text-xs font-bold text-indigo-400 uppercase">Completeness Analysis</span>
              <p className="mt-2 text-sm text-slate-300">Dataset exhibits 100% cell completeness with 0 null values across all 9 telemetry features.</p>
            </div>
            <div className="rounded-lg bg-slate-950 p-4 border border-slate-800">
              <span className="text-xs font-bold text-emerald-400 uppercase">Variance & Deadlock</span>
              <p className="mt-2 text-sm text-slate-300">All sensor telemetry channels display healthy dynamic variance without zero-variance flatlining.</p>
            </div>
          </div>
        </div>
      )}

      {activeTab === "validation" && <ValidationRuleTable results={sampleValidationResults} />}

      {activeTab === "history" && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-sm font-bold uppercase text-slate-300 mb-4">Historical Validation Executions</h3>
          <div className="space-y-3">
            {[
              { id: "val-run-1", version: "v1", score: 99.5, status: "PASSED", time: "Today at 08:30" },
              { id: "val-run-2", version: "v1", score: 99.5, status: "PASSED", time: "Yesterday at 14:15" },
            ].map((item) => (
              <div key={item.id} className="flex items-center justify-between rounded-lg bg-slate-950 p-4 border border-slate-800/80">
                <div>
                  <p className="font-semibold text-sm text-slate-200">Execution {item.id}</p>
                  <p className="text-xs text-slate-500">Version {item.version} • {item.time}</p>
                </div>
                <span className="font-bold text-sm text-emerald-400">{item.score}% Score</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
