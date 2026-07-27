"use client";

import React, { useState } from "react";
import { Plugin } from "@/types/plugin";
import { Puzzle, Filter, ArrowUpRight, Power, RefreshCw } from "lucide-react";
import Link from "next/link";

export default function PluginManagerPage() {
  const [filterType, setFilterType] = useState<string>("all");

  const [plugins, setPlugins] = useState<Plugin[]>([
    {
      id: "p-1",
      plugin_id: "sentinel.plugin.connector.snowflake",
      name: "Snowflake Cloud Connector",
      version: "1.2.0",
      author: "Sentinel AI SDK Team",
      description: "High throughput Snowflake ingestion connector plugin.",
      plugin_type: "connector",
      status: "enabled",
      entry_point: "examples.connector_plugin.main:SnowflakeConnectorPlugin",
      minimum_platform_version: "1.0.0",
      permissions: { permissions: ["network:read", "database:connect"] },
      created_at: "2026-07-27T08:00:00Z",
      installations: [],
    },
    {
      id: "p-2",
      plugin_id: "sentinel.plugin.rule.regex_anomaly",
      name: "Regex Anomaly Validation Rule",
      version: "1.0.1",
      author: "Sentinel AI SDK Team",
      description: "Custom regex string pattern validation rule plugin.",
      plugin_type: "validation_rule",
      status: "enabled",
      entry_point: "examples.validation_plugin.main:RegexAnomalyRulePlugin",
      minimum_platform_version: "1.0.0",
      permissions: { permissions: ["data:read"] },
      created_at: "2026-07-27T08:00:00Z",
      installations: [],
    },
    {
      id: "p-3",
      plugin_id: "sentinel.plugin.workflow.multi_cloud",
      name: "Multi-Cloud Ingestion Pipeline",
      version: "2.0.0",
      author: "Sentinel AI SDK Team",
      description: "Multi-cloud pipeline orchestrator workflow plugin.",
      plugin_type: "workflow",
      status: "disabled",
      entry_point: "examples.workflow_plugin.main:MultiCloudWorkflowPlugin",
      minimum_platform_version: "1.0.0",
      permissions: { permissions: ["workflow:execute", "job:create"] },
      created_at: "2026-07-27T08:00:00Z",
      installations: [],
    },
  ]);

  const togglePlugin = (plugin_id: string) => {
    setPlugins((prev) =>
      prev.map((p) => {
        if (p.plugin_id === plugin_id) {
          const nextStatus = p.status === "enabled" ? "disabled" : "enabled";
          return { ...p, status: nextStatus as any };
        }
        return p;
      })
    );
  };

  const filtered = plugins.filter((p) => {
    if (filterType !== "all" && p.plugin_type !== filterType) return false;
    return true;
  });

  return (
    <div className="space-y-8 p-8">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              Enterprise Plugin & Extension SDK
            </h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
              <Puzzle className="h-3.5 w-3.5" /> 3 Local Plugins Installed
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Extend Sentinel AI with custom Connectors, Validation Rules, Profiling Engines, Drift Detectors, Alerts, AI Analyzers, Recommendations, Forecasts, and Workflows without modifying core platform code.
          </p>
        </div>

        <button className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-500 shadow-md">
          <RefreshCw className="h-4 w-4" /> Rescan Local Plugins
        </button>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Total Installed Plugins</p>
          <div className="text-3xl font-extrabold font-mono text-white">3</div>
          <p className="text-xs text-slate-500">Local plugin manifests</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Active Enabled Plugins</p>
          <div className="text-3xl font-extrabold font-mono text-emerald-400">2</div>
          <p className="text-xs text-slate-500">Loaded in runtime memory</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Supported Plugin Types</p>
          <div className="text-3xl font-extrabold font-mono text-indigo-400">10</div>
          <p className="text-xs text-slate-500">SDK Extension Interfaces</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Security Audit</p>
          <div className="text-3xl font-extrabold font-mono text-slate-300">Clean</div>
          <p className="text-xs text-slate-500">0 unverified permissions</p>
        </div>
      </div>

      {/* Filters & Plugin List */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <h2 className="text-lg font-bold text-white">Discovered Extension Plugins</h2>

        <div className="flex items-center gap-3">
          <Filter className="h-4 w-4 text-slate-400" />
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none"
          >
            <option value="all">All Plugin Types</option>
            <option value="connector">Connector</option>
            <option value="validation_rule">Validation Rule</option>
            <option value="workflow">Workflow</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-lg overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="border-b border-slate-800 bg-slate-950/60 uppercase font-bold text-slate-400">
            <tr>
              <th className="py-3.5 px-4">Plugin ID</th>
              <th className="py-3.5 px-4">Plugin Name & Description</th>
              <th className="py-3.5 px-4">Type</th>
              <th className="py-3.5 px-4">Status</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {filtered.map((p) => (
              <tr key={p.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3.5 px-4 font-mono font-bold text-indigo-400">{p.plugin_id}</td>
                <td className="py-3.5 px-4 space-y-0.5">
                  <div className="font-bold text-slate-100">{p.name} <span className="text-[10px] text-slate-500 font-mono">v{p.version}</span></div>
                  <div className="text-slate-400 text-[11px] truncate max-w-md">{p.description}</div>
                </td>
                <td className="py-3.5 px-4 uppercase font-mono text-xs font-bold text-slate-300">{p.plugin_type}</td>
                <td className="py-3.5 px-4 uppercase font-mono font-bold">
                  <span className={p.status === "enabled" ? "text-emerald-400" : "text-slate-500"}>
                    {p.status}
                  </span>
                </td>
                <td className="py-3.5 px-4 text-right space-x-2">
                  <button
                    onClick={() => togglePlugin(p.plugin_id)}
                    className={`rounded px-3 py-1 text-[11px] font-semibold transition-colors ${
                      p.status === "enabled"
                        ? "bg-rose-500/10 text-rose-400 border border-rose-500/30 hover:bg-rose-500/20"
                        : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/20"
                    }`}
                  >
                    <Power className="h-3 w-3 inline mr-1" />
                    {p.status === "enabled" ? "Disable" : "Enable"}
                  </button>

                  <Link
                    href={`/plugins/${p.plugin_id}`}
                    className="rounded border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-[11px] font-semibold text-indigo-400 hover:bg-indigo-500/20 inline-block"
                  >
                    Config <ArrowUpRight className="h-3 w-3 inline" />
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
