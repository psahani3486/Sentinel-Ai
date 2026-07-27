"use client";

import React, { useState } from "react";

interface DatasetPreviewGridProps {
  rows: Record<string, any>[];
}

export const DatasetPreviewGrid: React.FC<DatasetPreviewGridProps> = ({ rows }) => {
  if (!rows || rows.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-8 text-center text-sm text-slate-500">
        No preview rows available for this dataset.
      </div>
    );
  }

  const columns = Object.keys(rows[0]);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>Showing sample preview ({rows.length} rows)</span>
        <span>{columns.length} Total Columns</span>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/80 shadow-lg">
        <table className="w-full text-left text-xs font-mono text-slate-300">
          <thead className="bg-slate-950 text-slate-400 uppercase border-b border-slate-800">
            <tr>
              <th className="px-4 py-3 text-slate-600">#</th>
              {columns.map((col) => (
                <th key={col} className="px-4 py-3 whitespace-nowrap font-bold text-slate-200">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {rows.map((row, idx) => (
              <tr key={idx} className="hover:bg-slate-800/50 transition-colors">
                <td className="px-4 py-2.5 text-slate-600 select-none">{idx + 1}</td>
                {columns.map((col) => {
                  const val = row[col];
                  const displayVal = val === null || val === undefined ? "null" : String(val);
                  const isNull = val === null || val === undefined;

                  return (
                    <td
                      key={col}
                      className={`px-4 py-2.5 whitespace-nowrap ${
                        isNull ? "text-rose-400/80 italic font-sans" : "text-slate-300"
                      }`}
                    >
                      {displayVal}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
