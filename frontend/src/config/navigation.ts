/**
 * Sentinel AI — Sidebar Navigation Configuration
 *
 * Defines all navigation items, their icons (as Lucide icon names),
 * route paths, and required roles for access control.
 */

import { UserRole } from "@/types/auth";

export interface NavItem {
  label: string;
  href: string;
  icon: string;
  roles: UserRole[];
  badge?: string;
  children?: NavItem[];
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

const ALL_ROLES = [
  UserRole.ADMIN,
  UserRole.DATA_ENGINEER,
  UserRole.ML_ENGINEER,
  UserRole.VIEWER,
];

const ENGINEER_ROLES = [
  UserRole.ADMIN,
  UserRole.DATA_ENGINEER,
  UserRole.ML_ENGINEER,
];

export const navigationConfig: NavSection[] = [
  {
    title: "Overview",
    items: [
      {
        label: "Dashboard",
        href: "/dashboard",
        icon: "LayoutDashboard",
        roles: ALL_ROLES,
      },
      {
        label: "Data Catalog",
        href: "/catalog",
        icon: "Database",
        roles: ALL_ROLES,
      },
    ],
  },
  {
    title: "Data Operations",
    items: [
      {
        label: "Datasets",
        href: "/datasets",
        icon: "Database",
        roles: ALL_ROLES,
      },
      {
        label: "Validations",
        href: "/validations",
        icon: "ShieldCheck",
        roles: ALL_ROLES,
      },
      {
        label: "Workflows",
        href: "/workflows",
        icon: "GitBranch",
        roles: ENGINEER_ROLES,
      },
    ],
  },
  {
    title: "Intelligence & Observability",
    items: [
      {
        label: "Alerts",
        href: "/alerts",
        icon: "AlertTriangle",
        roles: ALL_ROLES,
      },
      {
        label: "Incidents",
        href: "/incidents",
        icon: "AlertTriangle",
        roles: ALL_ROLES,
      },
      {
        label: "Data Drift",
        href: "/drift",
        icon: "Brain",
        roles: ALL_ROLES,
      },
      {
        label: "Risk Forecast",
        href: "/forecast",
        icon: "Brain",
        roles: ALL_ROLES,
      },
      {
        label: "AI Diagnostics",
        href: "/analysis",
        icon: "Brain",
        roles: ALL_ROLES,
      },
      {
        label: "Recommendations",
        href: "/recommendations",
        icon: "ShieldCheck",
        roles: ALL_ROLES,
      },
    ],
  },
  {
    title: "Administration",
    items: [
      {
        label: "Plugins & Extensions",
        href: "/plugins",
        icon: "Users",
        roles: [UserRole.ADMIN],
      },
      {
        label: "Policy Governance",
        href: "/policies",
        icon: "ShieldCheck",
        roles: [UserRole.ADMIN],
      },
      {
        label: "APM Telemetry",
        href: "/telemetry",
        icon: "Settings",
        roles: [UserRole.ADMIN],
      },
      {
        label: "Settings",
        href: "/settings",
        icon: "Settings",
        roles: [UserRole.ADMIN],
      },
    ],
  },
];
