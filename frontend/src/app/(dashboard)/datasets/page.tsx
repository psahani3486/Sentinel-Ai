"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Database, Plus, Search, Filter, ArrowRight, ShieldCheck } from "lucide-react";
import type { DatasetItem } from "@/types/dataset";

export default function DatasetsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedType, setSelectedType] = useState<string>("all");

  const [datasets] = useState<DatasetItem[]>([
    {
      id: "ds-ai4i-2020",
      name: "AI4I 2020 Predictive Maintenance Dataset",
      description: "Industrial synthetic maintenance dataset featuring 10,000 telemetry records.",
      dataset_type: "sensor_stream",
      connector_type: "industrial_sensor",
      is_active: true,
      created_at: "2026-07-26T08:00:00Z",
    },
    {
      id: "ds-nasa-turbofan",
      name: "NASA Turbofan Engine Degradation Dataset",
      description: "Run-to-failure sensor degradation trajectories for jet turbine propulsion engines.",
      dataset_type: "time_series",
      connector_type: "csv",
      is_active: true,
      created_at: "2026-07-26T08:15:00Z",
    },
    {
      id: "ds-secom-manufacturing",
      name: "SECOM Semiconductor Manufacturing Dataset",
      description: "590 sensor signals from semiconductor wafer manufacturing yield lines.",
      dataset_type: "tabular",
      connector_type: "postgresql",
      is_active: true,
      created_at: "2026-07-26T08:30:00Z",
    },
  ]);

  const filteredDatasets = datasets.filter((ds) => {
    const matchesSearch = ds.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (ds.description && ds.description.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = selectedType === "all" || ds.dataset_type === selectedType;
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-6 p-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Enterprise Datasets & Assets
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Catalog of industrial telemetry streams, database connectors, and batch tabular sources.
          </p>
        </div>
        <Link
          href="/datasets/upload"
          className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/20 hover:bg-indigo-500 transition-all"
        >
          <Plus className="h-4 w-4" /> Add New Dataset
        </Link>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search datasets by name or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-lg border border-slate-800 bg-slate-900/90 py-2 pl-9 pr-4 text-sm text-slate-200 placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
          />
        </div>

        <div className="flex items-center gap-3">
          <Filter className="h-4 w-4 text-slate-500" />
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="rounded-lg border border-slate-800 bg-slate-900 py-2 px-3 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
          >
            <option value="all">All Asset Types</option>
            <option value="sensor_stream">Sensor Stream</option>
            <option value="time_series">Time Series</option>
            <option value="tabular">Tabular</option>
          </select>
        </div>
      </div>

      {/* Datasets Table */}
      <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-xl">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-950/80 text-xs uppercase tracking-wider text-slate-400">
            <tr>
              <th className="px-6 py-4">Dataset Name</th>
              <th className="px-6 py-4">Dataset Type</th>
              <th className="px-6 py-4">Connector</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filteredDatasets.map((ds) => (
              <tr key={ds.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-start gap-3">
                    <div className="rounded-lg bg-indigo-500/10 p-2 text-indigo-400 border border-indigo-500/20 mt-0.5">
                      <Database className="h-4 w-4" />
                    </div>
                    <div>
                      <Link href={`/datasets/${ds.id}`} className="font-semibold text-slate-100 hover:text-indigo-400 transition-colors">
                        {ds.name}
                      </Link>
                      <p className="mt-0.5 text-xs text-slate-500 line-clamp-1">{ds.description}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center rounded-md bg-slate-800 px-2.5 py-1 text-xs font-medium text-slate-300">
                    {ds.dataset_type}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center rounded-md bg-indigo-500/10 px-2.5 py-1 text-xs font-mono text-indigo-300 border border-indigo-500/20">
                    {ds.connector_type}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
                    <ShieldCheck className="h-3.5 w-3.5" /> Active
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <Link
                    href={`/datasets/${ds.id}`}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-400 hover:text-indigo-300"
                  >
                    Explore <ArrowRight className="h-3.5 w-3.5" />
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
