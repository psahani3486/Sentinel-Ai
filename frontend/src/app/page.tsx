"use client";

/**
 * Root page — redirects to /dashboard if authenticated, /login if not.
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/hooks/use-auth";

export default function RootPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        router.replace("/dashboard");
      } else {
        router.replace("/login");
      }
    }
  }, [isAuthenticated, isLoading, router]);

  // Full-screen loading state
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <div
          className="flex h-14 w-14 items-center justify-center rounded-2xl"
          style={{
            background:
              "linear-gradient(135deg, var(--color-sentinel-blue), var(--color-sentinel-purple))",
          }}
        >
          <div className="spinner" style={{ borderTopColor: "white" }} />
        </div>
        <p
          className="text-sm"
          style={{ color: "var(--color-sentinel-text-muted)" }}
        >
          Loading Sentinel AI...
        </p>
      </div>
    </div>
  );
}
