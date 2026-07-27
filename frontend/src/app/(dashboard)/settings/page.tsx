"use client";

import React, { useState } from "react";
import { Settings, Shield, Sliders, Bell, Server } from "lucide-react";

export default function SettingsPage() {
  const [criticalPenalty, setCriticalPenalty] = useState(25);
  const [highPenalty, setHighPenalty] = useState(15);
  const [mediumPenalty, setMediumPenalty] = useState(10);
  const [lowPenalty, setLowPenalty] = useState(5);
  const [isSaved, setIsSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
  };

  return (
    <div className="mx-auto max-w-4xl space-y-8 p-8">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white">
          Platform Configuration & Settings
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Configure rule scoring penalty thresholds, SLA weighting formulas, and system parameters.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Scoring Penalties */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center gap-2 text-indigo-400">
            <Sliders className="h-5 w-5" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Severity Deductions & Penalty Weights
            </h3>
          </div>
          <p className="text-xs text-slate-400">
            Customize Quality Score deduction penalties subtracted when validation rules fail.
          </p>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase text-slate-400">CRITICAL Failure Penalty</label>
              <input
                type="number"
                value={criticalPenalty}
                onChange={(e) => setCriticalPenalty(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-4 py-2 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase text-slate-400">HIGH Failure Penalty</label>
              <input
                type="number"
                value={highPenalty}
                onChange={(e) => setHighPenalty(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-4 py-2 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase text-slate-400">MEDIUM Failure Penalty</label>
              <input
                type="number"
                value={mediumPenalty}
                onChange={(e) => setMediumPenalty(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-4 py-2 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase text-slate-400">LOW Failure Penalty</label>
              <input
                type="number"
                value={lowPenalty}
                onChange={(e) => setLowPenalty(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-800 bg-slate-950 px-4 py-2 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 space-y-4">
          <div className="flex items-center gap-2 text-indigo-400">
            <Server className="h-5 w-5" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Sentinel AI Platform Telemetry
            </h3>
          </div>
          <div className="grid grid-cols-2 gap-4 text-xs text-slate-400">
            <div className="rounded-lg bg-slate-950 p-3 border border-slate-800">
              <span>Backend API Version</span>
              <p className="mt-1 font-mono font-bold text-white">v1.0.0 (FastAPI 0.115)</p>
            </div>
            <div className="rounded-lg bg-slate-950 p-3 border border-slate-800">
              <span>Engine Rules Loaded</span>
              <p className="mt-1 font-mono font-bold text-emerald-400">22 Registered Rules</p>
            </div>
          </div>
        </div>

        <button
          type="submit"
          className="rounded-lg bg-indigo-600 px-6 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/20 hover:bg-indigo-500 transition-all"
        >
          {isSaved ? "Configuration Saved!" : "Save Settings"}
        </button>
      </form>
    </div>
  );
}
