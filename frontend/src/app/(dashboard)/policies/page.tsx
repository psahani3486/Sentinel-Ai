"use client";

import React, { useState } from "react";
import { PolicyDefinition, PolicyEvaluation } from "@/types/policy";
import { ShieldCheck, Play, Filter, ArrowUpRight, CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import { ComplianceMatrix } from "@/components/policies/ComplianceMatrix";
import { EvaluationTimeline } from "@/components/policies/EvaluationTimeline";
import Link from "next/link";

export default function PoliciesDashboardPage() {
  const [filterCategory, setFilterCategory] = useState<string>("all");

  const [policies, setPolicies] = useState<PolicyDefinition[]>([
    {
      id: "pol-1",
      policy_name: "Dataset Mandatory Ownership Governance Policy",
      category: "dataset_governance",
      severity: "high",
      description: "Requires dataset owner and steward assignment in catalog.",
      is_active: true,
      created_at: "2026-07-27T08:00:00Z",
    },
    {
      id: "pol-2",
      policy_name: "Zero Breaking Schema Changes Policy",
      category: "schema",
      severity: "critical",
      description: "Prevents unannounced column deletion or type mutation.",
      is_active: true,
      created_at: "2026-07-27T08:00:00Z",
    },
    {
      id: "pol-3",
      policy_name: "Critical Quality Contract Execution Policy",
      category: "validation",
      severity: "high",
      description: "Enforces 0 critical contract failures per execution batch.",
      is_active: true,
      created_at: "2026-07-27T08:00:00Z",
    },
    {
      id: "pol-4",
      policy_name: "Minimum 90% Quality Score Policy",
      category: "quality_threshold",
      severity: "high",
      description: "Triggers warning if dataset quality score falls below 90%.",
      is_active: true,
      created_at: "2026-07-27T08:00:00Z",
    },
    {
      id: "pol-5",
      policy_name: "PSI Feature Distribution Drift Boundary Policy",
      category: "drift_threshold",
      severity: "medium",
      description: "Alerts when PSI exceeds 0.25 threshold.",
      is_active: true,
      created_at: "2026-07-27T08:00:00Z",
    },
    {
      id: "pol-6",
      policy_name: "Workflow Maximum Execution SLA Policy",
      category: "workflow",
      severity: "medium",
      description: "Ensures pipeline DAG execution completes within 300 seconds.",
      is_active: true,
      created_at: "2026-07-27T08:00:00Z",
    },
    {
      id: "pol-7",
      policy_name: "Local Plugin Extension Security Sandboxing Policy",
      category: "plugin",
      severity: "high",
      description: "Blocks plugins requesting unverified root access permissions.",
      is_active: true,
      created_at: "2026-07-27T08:00:00Z",
    },
    {
      id: "pol-8",
      policy_name: "Data Classification Sensitivity Tier Policy",
      category: "catalog_governance",
      severity: "high",
      description: "Ensures security sensitivity tier is populated.",
      is_active: true,
      created_at: "2026-07-27T08:00:00Z",
    },
    {
      id: "pol-9",
      policy_name: "GDPR Data Retention Compliance Policy",
      category: "retention",
      severity: "critical",
      description: "Caps maximum data retention at 365 days.",
      is_active: true,
      created_at: "2026-07-27T08:00:00Z",
    },
    {
      id: "pol-10",
      policy_name: "Critical Incident Automated Escalation SLA Policy",
      category: "incident_escalation",
      severity: "critical",
      description: "Escalates unmitigated critical incidents open > 2 hours.",
      is_active: true,
      created_at: "2026-07-27T08:00:00Z",
    },
  ]);

  const mockEvaluations: PolicyEvaluation[] = [
    {
      id: "ev-1",
      policy_id: "pol-1",
      status: "pass",
      severity: "high",
      recommendation: "No action required.",
      evaluated_at: "2026-07-27T08:00:00Z",
      policy_definition: policies[0],
    },
    {
      id: "ev-2",
      policy_id: "pol-2",
      status: "pass",
      severity: "critical",
      recommendation: "No action required.",
      evaluated_at: "2026-07-27T08:00:00Z",
      policy_definition: policies[1],
    },
  ];

  const filtered = policies.filter((p) => {
    if (filterCategory !== "all" && p.category !== filterCategory) return false;
    return true;
  });

  return (
    <div className="space-y-8 p-8">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              Enterprise Policy Engine & Rule Governance
            </h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-indigo-500/10 px-2.5 py-1 text-xs font-semibold text-indigo-400 border border-indigo-500/20">
              <ShieldCheck className="h-3.5 w-3.5" /> 10 Active Policies
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">
            Centralized policy evaluation engine assessing governance rules, operational SLAs, schema contracts, security tiers, and incident escalation policies using the Specification Pattern.
          </p>
        </div>

        <button className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-bold text-white hover:bg-indigo-500 shadow-lg shadow-indigo-600/20">
          <Play className="h-4 w-4" /> Evaluate All Policies
        </button>
      </div>

      {/* Compliance Matrix */}
      <ComplianceMatrix passCount={10} warnCount={0} failCount={0} />

      {/* Category Filter & Table */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <h2 className="text-lg font-bold text-white">Enterprise Policy Rule Specifications</h2>

        <div className="flex items-center gap-3">
          <Filter className="h-4 w-4 text-slate-400" />
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs text-slate-200 focus:outline-none"
          >
            <option value="all">All Categories</option>
            <option value="dataset_governance">Dataset Governance</option>
            <option value="schema">Schema</option>
            <option value="validation">Validation</option>
            <option value="quality_threshold">Quality Threshold</option>
            <option value="drift_threshold">Drift Threshold</option>
            <option value="workflow">Workflow</option>
            <option value="plugin">Plugin</option>
            <option value="catalog_governance">Catalog Governance</option>
            <option value="retention">Retention</option>
            <option value="incident_escalation">Incident Escalation</option>
          </select>
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-lg overflow-hidden">
        <table className="w-full text-left text-xs">
          <thead className="border-b border-slate-800 bg-slate-950/60 uppercase font-bold text-slate-400">
            <tr>
              <th className="py-3.5 px-4">Policy Rule Name</th>
              <th className="py-3.5 px-4">Category</th>
              <th className="py-3.5 px-4">Severity</th>
              <th className="py-3.5 px-4">Description</th>
              <th className="py-3.5 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {filtered.map((p) => (
              <tr key={p.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3.5 px-4 font-bold text-slate-100">{p.policy_name}</td>
                <td className="py-3.5 px-4 uppercase font-mono font-bold text-indigo-400">{p.category}</td>
                <td className="py-3.5 px-4 uppercase font-mono font-bold text-rose-400">{p.severity}</td>
                <td className="py-3.5 px-4 text-slate-300">{p.description}</td>
                <td className="py-3.5 px-4 text-right">
                  <Link
                    href={`/policies/${p.id}`}
                    className="rounded border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-[11px] font-semibold text-indigo-400 hover:bg-indigo-500/20 inline-block"
                  >
                    View Rule <ArrowUpRight className="h-3 w-3 inline" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Audit Timeline */}
      <EvaluationTimeline evaluations={mockEvaluations} />
    </div>
  );
}
