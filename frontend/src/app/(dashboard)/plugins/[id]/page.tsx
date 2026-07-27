"use client";

import React from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, Puzzle, Terminal, FileCode } from "lucide-react";
import { Plugin } from "@/types/plugin";
import { PluginHealthCard } from "@/components/plugins/PluginHealthCard";
import { LifecycleTimeline } from "@/components/plugins/LifecycleTimeline";
import { PermissionViewer } from "@/components/plugins/PermissionViewer";
import Link from "next/link";

export default function PluginDetailPage() {
  const params = useParams();
  const pluginId = params.id as string;

  const mockPlugin: Plugin = {
    id: "p-1",
    plugin_id: decodeURIComponent(pluginId),
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
  };

  return (
    <div className="space-y-8 p-8">
      {/* Navigation Header */}
      <div>
        <Link
          href="/plugins"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:underline mb-2"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Plugin Manager
        </Link>
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            {mockPlugin.name}
          </h1>
          <span className="font-mono text-xs text-slate-500">• {mockPlugin.plugin_id}</span>
        </div>
      </div>

      {/* Plugin Health Metrics */}
      <PluginHealthCard plugin={mockPlugin} />

      {/* Lifecycle Timeline */}
      <LifecycleTimeline currentStatus={mockPlugin.status} />

      {/* Permissions Audit */}
      <PermissionViewer permissions={mockPlugin.permissions?.permissions || []} />

      {/* Manifest Viewer */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-3 font-mono text-xs">
        <span className="font-bold text-indigo-400 uppercase flex items-center gap-1.5">
          <FileCode className="h-4 w-4" /> plugin.yaml Manifest Specification
        </span>
        <pre className="p-4 rounded-lg border border-slate-800 bg-slate-950/80 text-slate-300 overflow-x-auto">
{`id: "${mockPlugin.plugin_id}"
name: "${mockPlugin.name}"
version: "${mockPlugin.version}"
author: "${mockPlugin.author}"
description: "${mockPlugin.description}"
plugin_type: "${mockPlugin.plugin_type}"
entry_point: "${mockPlugin.entry_point}"
minimum_platform_version: "${mockPlugin.minimum_platform_version}"
permissions:
  - "network:read"
  - "database:connect"`}
        </pre>
      </div>
    </div>
  );
}
