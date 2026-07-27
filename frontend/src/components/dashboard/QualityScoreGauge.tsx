"use client";

import React from "react";

interface QualityScoreGaugeProps {
  score: number;
  size?: number;
  strokeWidth?: number;
}

export const QualityScoreGauge: React.FC<QualityScoreGaugeProps> = ({
  score,
  size = 180,
  strokeWidth = 14,
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const normalizedScore = Math.max(0, Math.min(100, score));
  const offset = circumference - (normalizedScore / 100) * circumference;

  let scoreColor = "#10B981"; // Emerald green >= 90
  let badgeLabel = "EXCELLENT";
  if (normalizedScore < 70) {
    scoreColor = "#EF4444"; // Red < 70
    badgeLabel = "CRITICAL";
  } else if (normalizedScore < 90) {
    scoreColor = "#F59E0B"; // Amber < 90
    badgeLabel = "DEGRADED";
  }

  return (
    <div className="relative flex flex-col items-center justify-center">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#1F2937"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={scoreColor}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          fill="transparent"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center text-center">
        <span className="text-4xl font-extrabold tracking-tight text-white">
          {normalizedScore.toFixed(1)}
        </span>
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          / 100
        </span>
        <span
          className="mt-1 rounded-full px-2.5 py-0.5 text-[10px] font-bold tracking-wider uppercase"
          style={{
            backgroundColor: `${scoreColor}20`,
            color: scoreColor,
            border: `1px solid ${scoreColor}40`,
          }}
        >
          {badgeLabel}
        </span>
      </div>
    </div>
  );
};
