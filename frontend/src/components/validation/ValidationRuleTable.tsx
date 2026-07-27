"use client";

import React, { useState } from "react";
import { CheckCircle2, XCircle, AlertTriangle, ChevronDown, ChevronRight, Bug } from "lucide-react";
import type { RuleResultItem } from "@/types/validation";

interface ValidationRuleTableProps {
  results: RuleResultItem[];
}

export const ValidationRuleTable: React.FC<ValidationRuleTableProps> = ({ results }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "passed":
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="h-3.5 w-3.5" /> PASSED
          </span>
        );
      case "failed":
      case "error":
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-500/10 px-2.5 py-1 text-xs font-semibold text-rose-400 border border-rose-500/20">
            <XCircle className="h-3.5 w-3.5" /> FAILED
          </span>
        );
      case "warning":
        return (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/10 px-2.5 py-1 text-xs font-semibold text-amber-400 border border-amber-500/20">
            <AlertTriangle className="h-3.5 w-3.5" /> WARNING
          </span>
        );
      default:
        return <span className="text-xs text-slate-400">{status}</span>;
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
        return <span className="rounded px-2 py-0.5 text-[10px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30 uppercase">CRITICAL</span>;
      case "high":
        return <span className="rounded px-2 py-0.5 text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase">HIGH</span>;
      case "medium":
        return <span className="rounded px-2 py-0.5 text-[10px] font-bold bg-sky-500/20 text-sky-300 border border-sky-500/30 uppercase">MEDIUM</span>;
      default:
        return <span className="rounded px-2 py-0.5 text-[10px] font-bold bg-slate-800 text-slate-400 uppercase">LOW</span>;
    }
  };

  return (
    <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60 shadow-lg">
      <table className="w-full text-left text-sm text-slate-300">
        <thead className="bg-slate-950/80 text-xs uppercase tracking-wider text-slate-400">
          <tr>
            <th className="w-10 px-4 py-3.5"></th>
            <th className="px-4 py-3.5">Rule Identifier</th>
            <th className="px-4 py-3.5">Status</th>
            <th className="px-4 py-3.5">Severity</th>
            <th className="px-4 py-3.5">Score Impact</th>
            <th className="px-4 py-3.5">Execution Time</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60">
          {results.map((res) => {
            const isExpanded = expandedId === res.id;
            return (
              <React.Fragment key={res.id}>
                <tr
                  onClick={() => toggleExpand(res.id)}
                  className="cursor-pointer hover:bg-slate-800/40 transition-colors"
                >
                  <td className="px-4 py-3.5 text-slate-500">
                    {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                  </td>
                  <td className="px-4 py-3.5 font-mono text-sm font-semibold text-slate-100">
                    {res.rule_type}
                  </td>
                  <td className="px-4 py-3.5">{getStatusBadge(res.status)}</td>
                  <td className="px-4 py-3.5">{getSeverityBadge(res.severity)}</td>
                  <td className="px-4 py-3.5 font-mono text-xs text-rose-400 font-bold">
                    {res.score_impact > 0 ? `-${res.score_impact.toFixed(1)}` : "0.0"}
                  </td>
                  <td className="px-4 py-3.5 font-mono text-xs text-slate-400">
                    {res.execution_time_ms.toFixed(2)} ms
                  </td>
                </tr>

                {isExpanded && (
                  <tr className="bg-slate-950/60">
                    <td colSpan={6} className="px-6 py-4 space-y-3">
                      <div className="flex items-start gap-2 text-sm text-slate-200">
                        <Bug className="h-4 w-4 text-amber-400 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="font-semibold">{res.message}</p>
                          {res.affected_columns && res.affected_columns.length > 0 && (
                            <div className="mt-2 flex items-center gap-2">
                              <span className="text-xs text-slate-400">Affected Columns:</span>
                              <div className="flex flex-wrap gap-1">
                                {res.affected_columns.map((col) => (
                                  <span
                                    key={col}
                                    className="rounded bg-slate-800 px-2 py-0.5 font-mono text-xs text-indigo-300"
                                  >
                                    {col}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};
