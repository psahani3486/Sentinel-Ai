"use client";

import React from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, ShieldCheck, CheckCircle2, AlertTriangle, XCircle, Code } from "lucide-react";
import { PolicyDefinition, PolicyEvaluation } from "@/types/policy";
import { EvidenceViewer } from "@/components/policies/EvidenceViewer";
import Link from "next/link";

export default function PolicyDetailPage() {
  const params = useParams();
  const policyId = params.id as string;

  const mockPolicy: PolicyDefinition = {
    id: policyId,
    policy_name: "Dataset Mandatory Ownership Governance Policy",
    category: "dataset_governance",
    severity: "high",
    description: "Requires dataset owner and steward assignment in catalog.",
    rules_spec: { policy_id: "pol-dataset-gov-01", required_keys: ["owner", "steward"] },
    is_active: true,
    created_at: "2026-07-27T08:00:00Z",
  };

  const mockEvaluation: PolicyEvaluation = {
    id: "ev-01",
    policy_id: policyId,
    status: "pass",
    severity: "high",
    evidence: { owner: "Data Engineering Team", steward: "Data Governance Officer" },
    recommendation: "No action required.",
    evaluated_at: "2026-07-27T08:00:00Z",
    policy_definition: mockPolicy,
  };

  return (
    <div className="space-y-8 p-8">
      {/* Navigation Header */}
      <div>
        <Link
          href="/policies"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:underline mb-2"
        >
          <ArrowLeft className="h-3.5 w-3.5" /> Back to Enterprise Policy Dashboard
        </Link>
        <div className="flex items-center gap-3">
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            {mockPolicy.policy_name}
          </h1>
          <span className="font-mono text-xs text-slate-500">• {policyId}</span>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Category</p>
          <div className="text-xl font-extrabold font-mono text-indigo-400 uppercase">{mockPolicy.category}</div>
          <p className="text-xs text-slate-500">Specification Domain</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Severity Tier</p>
          <div className="text-xl font-extrabold font-mono text-rose-400 uppercase">{mockPolicy.severity}</div>
          <p className="text-xs text-slate-500">Enforcement Tier</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Latest Status</p>
          <div className="text-xl font-extrabold font-mono text-emerald-400 uppercase">{mockEvaluation.status}</div>
          <p className="text-xs text-slate-500">Specification Satisfied</p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-1">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Rule State</p>
          <div className="text-xl font-extrabold font-mono text-slate-100 uppercase">ACTIVE</div>
          <p className="text-xs text-slate-500">Evaluating</p>
        </div>
      </div>

      {/* Description & Rules Specification */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-3">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
            Policy Description & Recommendation
          </h3>
          <div className="space-y-3 text-xs text-slate-300">
            <p className="leading-relaxed">{mockPolicy.description}</p>
            <div className="rounded-lg bg-slate-950/80 p-4 border border-slate-800 space-y-1">
              <span className="font-bold text-indigo-400">Remediation Guidance:</span>
              <p className="text-slate-300">{mockEvaluation.recommendation}</p>
            </div>
          </div>
        </div>

        <EvidenceViewer evidence={mockEvaluation.evidence} />
      </div>
    </div>
  );
}
