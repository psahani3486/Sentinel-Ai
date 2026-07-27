"use client";

/**
 * Sentinel AI — Sidebar Navigation
 *
 * Collapsible sidebar with:
 * - Icon-only collapsed mode
 * - Role-based item visibility
 * - Active route highlighting
 * - Smooth expand/collapse animation
 * - Section grouping with labels
 */

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  AlertTriangle,
  Brain,
  ChevronLeft,
  ChevronRight,
  Database,
  GitBranch,
  LayoutDashboard,
  LogOut,
  Settings,
  ShieldCheck,
  Users,
  Zap,
} from "lucide-react";

import { navigationConfig, type NavItem } from "@/config/navigation";
import { useAuth } from "@/hooks/use-auth";
import { cn } from "@/lib/utils";

const iconMap: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  LayoutDashboard,
  ShieldCheck,
  GitBranch,
  Database,
  AlertTriangle,
  Brain,
  Users,
  Settings,
};

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const isActive = (href: string) => pathname === href;

  const isItemVisible = (item: NavItem) => {
    if (!user) return false;
    return item.roles.includes(user.role);
  };

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 flex h-screen flex-col border-r transition-all duration-300 ease-in-out",
        collapsed ? "w-[68px]" : "w-[260px]"
      )}
      style={{
        background: "var(--color-sidebar-bg)",
        borderColor: "var(--color-sentinel-border-subtle)",
      }}
    >
      {/* Logo Area */}
      <div
        className="flex h-16 items-center gap-3 border-b px-4"
        style={{ borderColor: "var(--color-sentinel-border-subtle)" }}
      >
        <div
          className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg"
          style={{
            background: "linear-gradient(135deg, var(--color-sentinel-blue), var(--color-sentinel-purple))",
          }}
        >
          <Zap size={16} className="text-white" />
        </div>
        {!collapsed && (
          <div className="flex flex-col">
            <span className="text-sm font-semibold" style={{ color: "var(--color-sentinel-text)" }}>
              Sentinel AI
            </span>
            <span className="text-[10px] font-medium tracking-wider uppercase" style={{ color: "var(--color-sentinel-text-muted)" }}>
              Industrial Platform
            </span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        {navigationConfig.map((section) => {
          const visibleItems = section.items.filter(isItemVisible);
          if (visibleItems.length === 0) return null;

          return (
            <div key={section.title} className="mb-6">
              {!collapsed && (
                <p
                  className="mb-2 px-3 text-[11px] font-semibold uppercase tracking-widest"
                  style={{ color: "var(--color-sentinel-text-muted)" }}
                >
                  {section.title}
                </p>
              )}
              <ul className="space-y-1">
                {visibleItems.map((item) => {
                  const Icon = iconMap[item.icon];
                  const active = isActive(item.href);

                  return (
                    <li key={item.href}>
                      <Link
                        href={item.badge ? "#" : item.href}
                        className={cn(
                          "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150",
                          active
                            ? "text-white"
                            : "hover:text-white",
                          collapsed && "justify-center px-2"
                        )}
                        style={{
                          background: active
                            ? "var(--color-sidebar-active)"
                            : "transparent",
                          color: active
                            ? "var(--color-sentinel-text)"
                            : "var(--color-sentinel-text-secondary)",
                          ...(item.badge ? { cursor: "default", opacity: 0.5 } : {}),
                        }}
                        onMouseEnter={(e) => {
                          if (!active) {
                            e.currentTarget.style.background = "var(--color-sidebar-hover)";
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (!active) {
                            e.currentTarget.style.background = "transparent";
                          }
                        }}
                        title={collapsed ? item.label : undefined}
                      >
                        {Icon && (
                          <Icon
                            size={18}
                            className={cn(
                              "flex-shrink-0",
                              active && "text-[var(--color-sentinel-blue)]"
                            )}
                          />
                        )}
                        {!collapsed && (
                          <>
                            <span className="flex-1">{item.label}</span>
                            {item.badge && (
                              <span
                                className="rounded px-1.5 py-0.5 text-[10px] font-semibold"
                                style={{
                                  background: "var(--color-sentinel-surface-overlay)",
                                  color: "var(--color-sentinel-text-muted)",
                                }}
                              >
                                {item.badge}
                              </span>
                            )}
                          </>
                        )}
                        {active && (
                          <div
                            className="absolute left-0 h-6 w-[3px] rounded-r"
                            style={{ background: "var(--color-sentinel-blue)" }}
                          />
                        )}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          );
        })}
      </nav>

      {/* Bottom Section */}
      <div
        className="border-t p-3"
        style={{ borderColor: "var(--color-sentinel-border-subtle)" }}
      >
        {/* User Info */}
        {user && !collapsed && (
          <div
            className="mb-2 flex items-center gap-3 rounded-lg px-3 py-2"
            style={{ background: "var(--color-sentinel-surface)" }}
          >
            <div
              className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full text-xs font-bold"
              style={{
                background: "linear-gradient(135deg, var(--color-sentinel-emerald), var(--color-sentinel-cyan))",
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
            <div className="flex-1 overflow-hidden">
              <p
                className="truncate text-sm font-medium"
                style={{ color: "var(--color-sentinel-text)" }}
              >
                {user.full_name}
              </p>
              <p
                className="truncate text-xs"
                style={{ color: "var(--color-sentinel-text-muted)" }}
              >
                {user.role.replace("_", " ")}
              </p>
            </div>
          </div>
        )}

        {/* Logout */}
        <button
          onClick={logout}
          className={cn(
            "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all",
            collapsed && "justify-center px-2"
          )}
          style={{ color: "var(--color-sentinel-text-secondary)" }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "var(--color-sidebar-hover)";
            e.currentTarget.style.color = "var(--color-sentinel-red)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "transparent";
            e.currentTarget.style.color = "var(--color-sentinel-text-secondary)";
          }}
          title={collapsed ? "Log out" : undefined}
        >
          <LogOut size={18} />
          {!collapsed && <span>Log out</span>}
        </button>

        {/* Collapse Toggle */}
        <button
          onClick={onToggle}
          className={cn(
            "mt-1 flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all",
            collapsed && "justify-center px-2"
          )}
          style={{ color: "var(--color-sentinel-text-muted)" }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = "var(--color-sidebar-hover)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = "transparent";
          }}
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          {!collapsed && <span>Collapse</span>}
        </button>
      </div>
    </aside>
  );
}
