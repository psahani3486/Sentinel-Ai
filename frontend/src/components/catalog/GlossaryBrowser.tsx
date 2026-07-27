"use client";

import React from "react";
import { GlossaryTerm } from "@/types/catalog";
import { BookOpen, Tag } from "lucide-react";

interface GlossaryBrowserProps {
  terms: GlossaryTerm[];
}

export const GlossaryBrowser: React.FC<GlossaryBrowserProps> = ({ terms }) => {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md shadow-lg space-y-4">
      <div>
        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-indigo-400" /> Business Glossary Browser
        </h3>
        <p className="text-xs text-slate-500">Standardized business metrics definitions and domain glossary terms</p>
      </div>

      <div className="space-y-3">
        {terms.map((t) => (
          <div key={t.id || t.term} className="rounded-lg border border-slate-800 bg-slate-950/80 p-4 space-y-1.5 font-mono text-xs">
            <div className="flex items-center justify-between text-indigo-400 font-bold">
              <span>{t.term}</span>
              <span className="text-[10px] text-slate-500 uppercase">{t.domain}</span>
            </div>

            <p className="text-slate-300 text-xs leading-relaxed">{t.definition}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
