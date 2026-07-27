"use client";

import React, { useState } from "react";
import { Upload, Database, CheckCircle, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function UploadDatasetPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<"file" | "database">("file");

  // File Upload Form State
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [datasetType, setDatasetType] = useState("sensor_stream");
  const [connectorType, setConnectorType] = useState("industrial_sensor");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Database Form State
  const [dbName, setDbName] = useState("");
  const [dbHost, setDbHost] = useState("localhost");
  const [dbPort, setDbPort] = useState(5432);
  const [dbDatabase, setDbDatabase] = useState("");
  const [dbUsername, setDbUsername] = useState("");
  const [dbPassword, setDbPassword] = useState("");
  const [dbTable, setDbTable] = useState("");

  const handleFileUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !file) return;

    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      router.push("/datasets");
    }, 1200);
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6 p-8">
      {/* Back Link */}
      <Link href="/datasets" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-slate-200">
        <ArrowLeft className="h-4 w-4" /> Back to Datasets Catalog
      </Link>

      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white">
          Ingest & Register Data Connector
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Upload industrial sensor files (CSV/telemetry) or register external PostgreSQL / MySQL database sources.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-800">
        <button
          onClick={() => setActiveTab("file")}
          className={`flex items-center gap-2 border-b-2 py-3 px-6 text-sm font-semibold transition-all ${
            activeTab === "file"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Upload className="h-4 w-4" /> Upload Industrial File
        </button>
        <button
          onClick={() => setActiveTab("database")}
          className={`flex items-center gap-2 border-b-2 py-3 px-6 text-sm font-semibold transition-all ${
            activeTab === "database"
              ? "border-indigo-500 text-indigo-400"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Database className="h-4 w-4" /> Register Database Connection
        </button>
      </div>

      {/* File Upload Form */}
      {activeTab === "file" ? (
        <form onSubmit={handleFileUploadSubmit} className="space-y-6 rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-xl">
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-300">Dataset Name *</label>
            <input
              type="text"
              required
              placeholder="e.g. AI4I 2020 Predictive Maintenance Telemetry"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-300">Description</label>
            <textarea
              rows={3}
              placeholder="Provide context regarding sensor channels, plant location, or sampling frequency..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-300">Dataset Domain Type</label>
              <select
                value={datasetType}
                onChange={(e) => setDatasetType(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
              >
                <option value="sensor_stream">Sensor Stream (Industrial IoT)</option>
                <option value="time_series">Time Series Trajectories</option>
                <option value="tabular">Batch Tabular Dataset</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-300">Target Connector Protocol</label>
              <select
                value={connectorType}
                onChange={(e) => setConnectorType(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
              >
                <option value="industrial_sensor">Industrial Sensor Protocol</option>
                <option value="csv">Standard CSV Connector</option>
              </select>
            </div>
          </div>

          {/* File Dropzone */}
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-300">Dataset File *</label>
            <div className="flex justify-center rounded-xl border-2 border-dashed border-slate-800 bg-slate-950/80 px-6 py-10 transition-colors hover:border-indigo-500/50">
              <div className="text-center">
                <Upload className="mx-auto h-10 w-10 text-slate-500" />
                <div className="mt-3 flex text-sm text-slate-400">
                  <label className="relative cursor-pointer font-semibold text-indigo-400 hover:text-indigo-300">
                    <span>Upload a file</span>
                    <input
                      type="file"
                      accept=".csv,.txt,.json"
                      onChange={(e) => setFile(e.target.files ? e.target.files[0] : null)}
                      className="sr-only"
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs text-slate-500 mt-1">CSV, TSV, or JSON up to 500MB</p>
                {file && (
                  <p className="mt-3 inline-flex items-center gap-1.5 rounded-full bg-indigo-500/10 px-3 py-1 text-xs font-semibold text-indigo-300 border border-indigo-500/30">
                    <CheckCircle className="h-3.5 w-3.5" /> Selected: {file.name}
                  </p>
                )}
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting || !name || !file}
            className="w-full rounded-lg bg-indigo-600 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/20 hover:bg-indigo-500 disabled:opacity-50 transition-all"
          >
            {isSubmitting ? "Ingesting & Profiling Dataset..." : "Upload & Register Dataset"}
          </button>
        </form>
      ) : (
        /* Database Registration Form */
        <form onSubmit={(e) => { e.preventDefault(); router.push("/datasets"); }} className="space-y-6 rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-xl">
          <div className="space-y-2">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-300">Connection Label *</label>
            <input
              type="text"
              required
              placeholder="e.g. Production Line 4 Postgres Yield Table"
              value={dbName}
              onChange={(e) => setDbName(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="space-y-2 sm:col-span-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-300">Database Host *</label>
              <input
                type="text"
                required
                value={dbHost}
                onChange={(e) => setDbHost(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-300">Port *</label>
              <input
                type="number"
                required
                value={dbPort}
                onChange={(e) => setDbPort(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-300">Database Name *</label>
              <input
                type="text"
                required
                placeholder="manufacturing_db"
                value={dbDatabase}
                onChange={(e) => setDbDatabase(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-slate-300">Table Name *</label>
              <input
                type="text"
                required
                placeholder="sensor_telemetry_logs"
                value={dbTable}
                onChange={(e) => setDbTable(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-4 py-2.5 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full rounded-lg bg-indigo-600 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/20 hover:bg-indigo-500 transition-all"
          >
            Test Connection & Register Database
          </button>
        </form>
      )}
    </div>
  );
}
