"use client";

import React, { useState } from "react";
import { Key, Hash, AlignLeft, Calendar, Search } from "lucide-react";
import type { ColumnSchema } from "@/types/dataset";

interface SchemaExplorerProps {
  columns: ColumnSchema[];
}

export const SchemaExplorer: React.FC<SchemaExplorerProps> = ({ columns }) => {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredColumns = columns.filter((col) =>
    col.column_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getTypeIcon = (typeStr: string) => {
    const t = typeStr.toLowerCase();
    if (t.includes("int") || t.includes("float") || t.includes("num") || t.includes("double")) {
      return <Hash className="h-4 w-4 text-emerald-400" />;
    }
    if (t.includes("date") || t.includes("time")) {
      return <Calendar className="h-4 w-4 text-amber-400" />;
    }
    return <AlignLeft className="h-4 w-4 text-sky-400" />;
  };

  return (
    <div className="space-y-4">
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
        <input
          type="text"
          placeholder="Search columns..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full rounded-lg border border-slate-800 bg-slate-900/90 py-2 pl-9 pr-4 text-sm text-slate-200 placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
        />
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60 shadow-lg">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-950/80 text-xs uppercase tracking-wider text-slate-400">
            <tr>
              <th className="px-5 py-3.5">Column Name</th>
              <th className="px-5 py-3.5">Data Type</th>
              <th className="px-5 py-3.5">Nullability</th>
              <th className="px-5 py-3.5">Key Type</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filteredColumns.map((col) => (
              <tr key={col.column_name} className="hover:bg-slate-800/40 transition-colors">
                <td className="px-5 py-3.5 font-mono text-sm font-semibold text-slate-100 flex items-center gap-2">
                  {getTypeIcon(col.data_type)}
                  {col.column_name}
                </td>
                <td className="px-5 py-3.5">
                  <span className="inline-flex items-center rounded-md bg-slate-800/80 px-2 py-1 font-mono text-xs text-indigo-300">
                    {col.data_type}
                  </span>
                </td>
                <td className="px-5 py-3.5">
                  {col.is_nullable ? (
                    <span className="text-xs text-slate-400">Nullable</span>
                  ) : (
                    <span className="rounded px-2 py-0.5 text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      NOT NULL
                    </span>
                  )}
                </td>
                <td className="px-5 py-3.5">
                  {col.is_primary_key ? (
                    <span className="inline-flex items-center gap-1 rounded bg-indigo-500/20 px-2 py-0.5 text-xs font-bold text-indigo-400 border border-indigo-500/30">
                      <Key className="h-3 w-3" /> PK
                    </span>
                  ) : (
                    <span className="text-xs text-slate-600">—</span>
                  )}
                </td>
              </tr>
            ))}
            {filteredColumns.length === 0 && (
              <tr>
                <td colSpan={4} className="px-5 py-8 text-center text-sm text-slate-500">
                  No schema columns match your search term.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
