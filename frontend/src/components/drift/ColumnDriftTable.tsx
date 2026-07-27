"use client";

import React, { useState } from "react";
import { DriftResult } from "@/types/drift";
import { CheckCircle2, AlertOctagon, Filter } from "lucide-react";

interface ColumnDriftTableProps {
  results: DriftResult[];
}

export const ColumnDriftTable: React.FC<ColumnDriftTableProps> = ({ results }) => {
  const [filterDriftedOnly, setFilterDriftedOnly] = useState(false);

  const filtered = filterDriftedOnly
    ? results.filter((r) => r.drift_detected)
    : results;

  const getSeverityBadge = (sev: string) => {
    switch (sev.toLowerCase()) {
      case "critical":
      case "high":
        return "bg-rose-500/10 text-rose-400 border-rose-500/20";
      case "medium":
        return "bg-amber-500/10 text-amber-400 border-amber-500/20";
      case "low":
        return "bg-sky-500/10 text-sky-400 border-sky-500/20";
      default:
        return "bg-slate-500/10 text-slate-400 border-slate-500/20";
    }
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-md shadow-lg overflow-hidden space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
            Per-Column Feature Drift Analysis
          </h3>
          <p className="text-xs text-slate-500">Individual statistical detector scores and threshold evaluations</p>
        </div>

        <button
          onClick={() => setFilterDriftedOnly(!filterDriftedOnly)}
          className={`inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${
            filterDriftedOnly
              ? "border-indigo-500 bg-indigo-500/10 text-indigo-400"
              : "border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700"
          }`}
        >
          <Filter className="h-3.5 w-3.5" />
          {filterDriftedOnly ? "Showing Drifted Only" : "Show All Columns"}
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="border-b border-slate-800 bg-slate-950/60 uppercase font-bold text-slate-400">
            <tr>
              <th className="py-3 px-4">Column Name</th>
              <th className="py-3 px-4">Type</th>
              <th className="py-3 px-4">Detector</th>
              <th className="py-3 px-4 text-center">Status</th>
              <th className="py-3 px-4 text-right">Drift Score</th>
              <th className="py-3 px-4 text-right">Threshold</th>
              <th className="py-3 px-4">Severity</th>
              <th className="py-3 px-4">Explanation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-300">
            {filtered.map((r) => (
              <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3 px-4 font-mono font-semibold text-slate-100">{r.column_name}</td>
                <td className="py-3 px-4 uppercase text-[10px] font-bold text-slate-400">{r.column_type}</td>
                <td className="py-3 px-4 font-mono text-slate-300">{r.detector_type.toUpperCase()}</td>
                <td className="py-3 px-4 text-center">
                  {r.drift_detected ? (
                    <span className="inline-flex items-center gap-1 rounded bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 text-[10px] font-bold text-rose-400">
                      <AlertOctagon className="h-3 w-3" /> DRIFT
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 rounded bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-400">
                      <CheckCircle2 className="h-3 w-3" /> STABLE
                    </span>
                  )}
                </td>
                <td className="py-3 px-4 text-right font-mono font-bold text-slate-100">{r.drift_score.toFixed(4)}</td>
                <td className="py-3 px-4 text-right font-mono text-slate-400">{r.threshold.toFixed(2)}</td>
                <td className="py-3 px-4">
                  <span className={`rounded border px-2 py-0.5 text-[10px] font-bold uppercase ${getSeverityBadge(r.severity)}`}>
                    {r.severity}
                  </span>
                </td>
                <td className="py-3 px-4 text-slate-400 max-w-xs truncate">{r.explanation}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
