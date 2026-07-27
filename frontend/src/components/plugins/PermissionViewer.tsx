"use client";

import React from "react";
import { Shield, Key } from "lucide-react";

interface PermissionViewerProps {
  permissions?: string[];
}

export const PermissionViewer: React.FC<PermissionViewerProps> = ({ permissions = [] }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <Shield className="h-4 w-4 text-emerald-400" /> Declared Permissions Security Audit
        </h3>
        <p className="text-xs text-slate-500">Platform scope capabilities declared in plugin.yaml</p>
      </div>

      <div className="flex flex-wrap gap-2 font-mono text-xs">
        {permissions.map((perm) => (
          <span
            key={perm}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 font-bold"
          >
            <Key className="h-3.5 w-3.5 text-indigo-400" /> {perm}
          </span>
        ))}
        {permissions.length === 0 && (
          <span className="text-xs text-slate-500">No special permissions requested.</span>
        )}
      </div>
    </div>
  );
};
