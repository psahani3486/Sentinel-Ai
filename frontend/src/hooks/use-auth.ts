"use client";

/**
 * Sentinel AI — useAuth Hook
 *
 * Convenience hook for consuming the AuthContext.
 * Throws if used outside of AuthProvider.
 */

import { useContext } from "react";

import { AuthContext } from "@/providers/auth-provider";

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }

  return context;
}
