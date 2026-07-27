"use client";

import React, { useState } from "react";
import { CatalogAsset, GlossaryTerm, GovernancePolicy } from "@/types/catalog";
import { Database, Filter, ArrowUpRight, ShieldCheck, BookOpen, Shield } from "lucide-react";
import { GlossaryBrowser } from "@/components/catalog/GlossaryBrowser";
import { GovernanceDashboard } from "@/components/catalog/GovernanceDashboard";
import Link from "next/link";

export default function CatalogExplorerPage() {
  const [filterDomain, setFilterDomain] = useState<string>("all");

  const [assets, setAssets] = useState<CatalogAsset[]>([
    {
      id: "cat-1",
      name: "Industrial Sensor Telemetry Stream",
      asset_type: "dataset",
      domain: "Industrial IoT",
      owner: "Data Engineering Team",
      steward: "Data Governance Officer",
      business_description: "Primary operational telemetry stream capturing real-time industrial sensor readings.",
      technical_description: "PostgreSQL database table with automated quality contract checks.",
      sensitivity: "internal",
      retention_period_days: 365,
      lifecycle_status: "active",
      tags: { tags: ["iot", "telemetry", "production"] },
      classifications: { classifications: ["Operational Data", "SLA Critical"] },
      created_at: "2026-07-27T08:00:00Z",
      outgoing_lineages: [],
      incoming_lineages: [],
    },
    {
      id: "cat-2",
      name: "End-to-End Incident Investigation Pipeline",
      asset_type: "pipeline",
      domain: "Observability",
      owner: "Platform Operations",
      steward: "SRE Lead",
      business_description: "Automated DAG pipeline executing cross-module telemetry ingestion and RCA.",
      technical_description: "Airflow-style 9-step DAG execution pipeline.",
      sensitivity: "internal",
      retention_period_days: 90,
      lifecycle_status: "active",
      tags: { tags: ["pipeline", "workflow", "dag"] },
      classifications: { classifications: ["Automated Pipeline"] },
      created_at: "2026-07-27T08:00:00Z",
      outgoing_lineages: [],
      incoming_lineages: [],
    },
  ]);

  const mockTerms: GlossaryTerm[] = [
    {
      id: "t-1",
      term: "Data Quality SLA",
      definition: "Contractual threshold requiring at least 95% valid sensor observations per ingestion batch.",
      domain: "Industrial IoT",
      created_at: "2026-07-27T08:00:00Z",
    },
  ];

  const mockPolicies: GovernancePolicy[] = [
    {
      id: "pol-1",
      policy_name: "GDPR / PII Data Retention Policy",
      category: "Data Governance",
      compliance_status: "COMPLIANT",
      created_at: "2026-07-27T08:00:00Z",
    },
  ];

  const filtered = assets.filter((a) => {
    if (filterDomain !== "all" && a.domain !== filterDomain) return false;
    return true;
  });

  return (
    <div className="space-y-8 p-8">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              Enterprise Data Catalog, Lineage & Governance Platform
            </h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-indigo-500/10 px-2.5 py-1 text-xs font-semibold text-indigo-400 border border-indigo-500/20">
              <Database className="h-3.5 w-3.5" /> 2 Cataloged Assets
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Enterprise metadata catalog tracking datasets, asset ownership, business glossary terms, governance policies, and cross-layer lineage DAG graphs.
          </p>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Cataloged Assets</p>
          <div className="text-3xl font-extrabold font-mono text-white">2</div>
          <p className="text-xs text-slate-500">Datasets & Pipelines</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Business Glossary Terms</p>
          <div className="text-3xl font-extrabold font-mono text-indigo-400">1</div>
          <p className="text-xs text-slate-500">Standardized metrics</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Governance Compliance</p>
          <div className="text-3xl font-extrabold font-mono text-emerald-400">100%</div>
          <p className="text-xs text-slate-500">1/1 Policies Compliant</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Lineage DAG Edges</p>
          <div className="text-3xl font-extrabold font-mono text-amber-400">1</div>
          <p className="text-xs text-slate-500">Active dependencies</p>
        </div>
      </div>

      {/* Filters & Catalog Asset Log */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <h2 className="text-lg font-bold text-white">Metadata Asset Explorer</h2>

        <div className="flex items-center gap-3">
          <Filter className="h-4 w-4 text-slate-400" />
          <select
            value={filterDomain}
            onChange={(e) => setFilterDomain(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none"
          >
            <option value="all">All Domains</option>
            <option value="Industrial IoT">Industrial IoT</option>
            <option value="Observability">Observability</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-lg overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="border-b border-slate-800 bg-slate-950/60 uppercase font-bold text-slate-400">
            <tr>
              <th className="py-3.5 px-4">Asset Name</th>
              <th className="py-3.5 px-4">Type</th>
              <th className="py-3.5 px-4">Domain</th>
              <th className="py-3.5 px-4">Owner & Steward</th>
              <th className="py-3.5 px-4">Sensitivity</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {filtered.map((a) => (
              <tr key={a.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3.5 px-4 font-bold text-slate-100">{a.name}</td>
                <td className="py-3.5 px-4 uppercase font-mono font-bold text-indigo-400">{a.asset_type}</td>
                <td className="py-3.5 px-4 text-slate-300">{a.domain}</td>
                <td className="py-3.5 px-4 text-slate-400 space-y-0.5">
                  <div className="font-bold text-slate-200">{a.owner}</div>
                  <div className="text-[10px] text-slate-500">{a.steward}</div>
                </td>
                <td className="py-3.5 px-4 uppercase font-mono font-bold text-emerald-400">{a.sensitivity}</td>
                <td className="py-3.5 px-4 text-right">
                  <Link
                    href={`/catalog/${a.id}`}
                    className="rounded border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-[11px] font-semibold text-indigo-400 hover:bg-indigo-500/20 inline-block"
                  >
                    View Lineage <ArrowUpRight className="h-3 w-3 inline" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Business Glossary & Governance Dashboard Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <GlossaryBrowser terms={mockTerms} />
        <GovernanceDashboard policies={mockPolicies} />
      </div>
    </div>
  );
}
