"use client";

/**
 * Sentinel AI — Top Navigation Bar
 *
 * Horizontal header with:
 * - Breadcrumb navigation
 * - System health status indicator
 * - Search placeholder
 * - User avatar with role badge
 */

import { Bell, Search } from "lucide-react";
import { usePathname } from "next/navigation";

import { useAuth } from "@/hooks/use-auth";
import { cn, formatRole } from "@/lib/utils";

interface TopNavProps {
  sidebarCollapsed: boolean;
}

export function TopNav({ sidebarCollapsed }: TopNavProps) {
  const pathname = usePathname();
  const { user } = useAuth();

  const getBreadcrumb = () => {
    const segments = pathname.split("/").filter(Boolean);
    return segments.map((seg) =>
      seg
        .split("-")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ")
    );
  };

  const breadcrumb = getBreadcrumb();

  return (
    <header
      className={cn(
        "fixed right-0 top-0 z-30 flex h-16 items-center justify-between border-b px-6 transition-all duration-300",
        sidebarCollapsed ? "left-[68px]" : "left-[260px]"
      )}
      style={{
        background: "rgba(10, 10, 15, 0.8)",
        backdropFilter: "blur(12px)",
        borderColor: "var(--color-sentinel-border-subtle)",
      }}
    >
      {/* Left: Breadcrumb */}
      <div className="flex items-center gap-2">
        {breadcrumb.map((segment, index) => (
          <div key={segment} className="flex items-center gap-2">
            {index > 0 && (
              <span style={{ color: "var(--color-sentinel-text-muted)" }}>/</span>
            )}
            <span
              className={cn(
                "text-sm",
                index === breadcrumb.length - 1
                  ? "font-semibold"
                  : "font-normal"
              )}
              style={{
                color:
                  index === breadcrumb.length - 1
                    ? "var(--color-sentinel-text)"
                    : "var(--color-sentinel-text-secondary)",
              }}
            >
              {segment}
            </span>
          </div>
        ))}
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-4">
        {/* System Status */}
        <div className="flex items-center gap-2 rounded-lg px-3 py-1.5"
          style={{ background: "var(--color-sentinel-surface)" }}
        >
          <span className="status-dot status-dot-healthy" />
          <span
            className="text-xs font-medium"
            style={{ color: "var(--color-sentinel-emerald)" }}
          >
            System Online
          </span>
        </div>

        {/* Search */}
        <button
          className="flex h-9 items-center gap-2 rounded-lg border px-3 transition-all"
          style={{
            borderColor: "var(--color-sentinel-border)",
            color: "var(--color-sentinel-text-muted)",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.borderColor = "var(--color-sentinel-blue)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.borderColor = "var(--color-sentinel-border)";
          }}
        >
          <Search size={14} />
          <span className="text-xs">Search...</span>
          <kbd
            className="ml-4 rounded px-1.5 py-0.5 text-[10px]"
            style={{
              background: "var(--color-sentinel-surface-raised)",
              color: "var(--color-sentinel-text-muted)",
            }}
          >
            ⌘K
          </kbd>
        </button>

        {/* Notifications */}
        <button
          className="relative flex h-9 w-9 items-center justify-center rounded-lg transition-all"
          style={{ color: "var(--color-sentinel-text-secondary)" }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "var(--color-sentinel-surface-raised)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "transparent";
          }}
        >
          <Bell size={18} />
          <span
            className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full"
            style={{ background: "var(--color-sentinel-blue)" }}
          />
        </button>

        {/* User Avatar */}
        {user && (
          <div className="flex items-center gap-3">
            <div className="hidden flex-col items-end md:flex">
              <span
                className="text-sm font-medium"
                style={{ color: "var(--color-sentinel-text)" }}
              >
                {user.full_name}
              </span>
              <span
                className="text-[11px]"
                style={{ color: "var(--color-sentinel-text-muted)" }}
              >
                {formatRole(user.role)}
              </span>
            </div>
            <div
              className="flex h-9 w-9 items-center justify-center rounded-full text-xs font-bold"
              style={{
                background:
                  "linear-gradient(135deg, var(--color-sentinel-blue), var(--color-sentinel-purple))",
                color: "white",
              }}
            >
              {user.full_name
                .split(" ")
                .map((n) => n[0])
                .join("")
                .toUpperCase()
                .slice(0, 2)}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
