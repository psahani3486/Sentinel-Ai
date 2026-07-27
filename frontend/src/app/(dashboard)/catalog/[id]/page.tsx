"use client";

import React from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, Database, ShieldCheck, User, Calendar, Tag } from "lucide-react";
import { CatalogAsset } from "@/types/catalog";
import { InteractiveLineageGraph } from "@/components/catalog/InteractiveLineageGraph";
import Link from "next/link";

export default function CatalogDetailPage() {
  const params = useParams();
  const assetId = params.id as string;

  const mockAsset: CatalogAsset = {
    id: assetId,
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
  };

  return (
    <div className="space-y-8 p-8">
      {/* Navigation Header */}
      <div>
        <Link
          href="/catalog"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:underline mb-2"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Metadata Catalog Explorer
        </Link>
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            {mockAsset.name}
          </h1>
          <span className="font-mono text-xs text-slate-500">• {assetId}</span>
        </div>
      </div>

      {/* Overview Metadata Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Asset Owner & Steward</p>
          <div className="text-sm font-bold text-slate-200">{mockAsset.owner}</div>
          <p className="text-xs text-slate-500">Steward: {mockAsset.steward}</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Security Sensitivity</p>
          <div className="text-xl font-extrabold font-mono text-emerald-400 uppercase">{mockAsset.sensitivity}</div>
          <p className="text-xs text-slate-500">Internal Data Classification</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Retention Period</p>
          <div className="text-3xl font-extrabold font-mono text-indigo-400">{mockAsset.retention_period_days} Days</div>
          <p className="text-xs text-slate-500">GDPR Compliance Policy</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Lifecycle Governance</p>
          <div className="text-xl font-extrabold font-mono text-slate-200 uppercase">{mockAsset.lifecycle_status}</div>
          <p className="text-xs text-slate-500">Production Asset</p>
        </div>
      </div>

      {/* Interactive Lineage Graph Component */}
      <InteractiveLineageGraph assetName={mockAsset.name} />

      {/* Metadata Descriptions & Tags */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-3">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
            Business & Technical Descriptions
          </h3>
          <div className="space-y-2 text-xs text-slate-300">
            <div>
              <span className="font-bold text-indigo-400">Business Summary:</span>
              <p className="mt-1 leading-relaxed">{mockAsset.business_description}</p>
            </div>
            <div>
              <span className="font-bold text-indigo-400">Technical Details:</span>
              <p className="mt-1 leading-relaxed">{mockAsset.technical_description}</p>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
            Classifications & Tags
          </h3>
          <div className="space-y-3 font-mono text-xs">
            <div className="space-y-1">
              <span className="text-[10px] text-slate-500 uppercase">Tags</span>
              <div className="flex flex-wrap gap-2">
                {mockAsset.tags?.tags?.map((t) => (
                  <span key={t} className="px-2.5 py-1 rounded bg-slate-800 text-indigo-400 font-bold border border-slate-700">
                    #{t}
                  </span>
                ))}
              </div>
            </div>

            <div className="space-y-1">
              <span className="text-[10px] text-slate-500 uppercase">Classifications</span>
              <div className="flex flex-wrap gap-2">
                {mockAsset.classifications?.classifications?.map((c) => (
                  <span key={c} className="px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/30">
                    {c}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
