"use client";

import React from "react";
import { Alert } from "@/types/alert";
import { Bell, X, AlertOctagon, CheckCircle2, ShieldAlert, ArrowUpRight } from "lucide-react";
import Link from "next/link";

interface NotificationDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  alerts: Alert[];
}

export const NotificationDrawer: React.FC<NotificationDrawerProps> = ({
  isOpen,
  onClose,
  alerts,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-950/60 backdrop-blur-sm transition-opacity">
      <div className="fixed inset-y-0 right-0 flex max-w-full pl-10">
        <div className="w-screen max-w-md bg-slate-900 border-l border-slate-800 p-6 space-y-6 shadow-2xl flex flex-col justify-between">
          <div className="space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div className="flex items-center gap-2">
                <Bell className="h-5 w-5 text-indigo-400" />
                <h2 className="text-lg font-bold text-white">Live Incident Notifications</h2>
              </div>
              <button
                onClick={onClose}
                className="rounded p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-3 overflow-y-auto max-h-[70vh] pr-1">
              {alerts.length === 0 ? (
                <div className="text-center py-12 text-slate-500 text-sm space-y-2">
                  <CheckCircle2 className="h-8 w-8 mx-auto text-emerald-400" />
                  <p>All system components healthy. No active alerts.</p>
                </div>
              ) : (
                alerts.map((alt) => (
                  <div
                    key={alt.id}
                    className="rounded-xl border border-slate-800 bg-slate-950/80 p-4 space-y-2 relative group hover:border-slate-700 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold uppercase rounded px-2 py-0.5 border bg-rose-500/10 text-rose-400 border-rose-500/20">
                        <AlertOctagon className="h-3 w-3" /> {alt.severity}
                      </span>
                      <span className="text-[10px] font-mono text-slate-500">
                        {alt.occurrence_count}x occurrences
                      </span>
                    </div>

                    <h4 className="text-sm font-semibold text-slate-200">{alt.title}</h4>
                    <p className="text-xs text-slate-400 line-clamp-2">{alt.description}</p>

                    <div className="pt-2 flex items-center justify-between text-[11px] text-slate-500 border-t border-slate-800/60">
                      <span>{new Date(alt.last_seen_at).toLocaleTimeString()}</span>
                      <Link
                        href={`/alerts/${alt.id}`}
                        onClick={onClose}
                        className="inline-flex items-center gap-1 font-semibold text-indigo-400 hover:underline"
                      >
                        Inspect <ArrowUpRight className="h-3 w-3" />
                      </Link>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800 text-center">
            <Link
              href="/alerts"
              onClick={onClose}
              className="text-xs font-semibold text-indigo-400 hover:underline block w-full py-2"
            >
              Open Full Alert Center Dashboard
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
