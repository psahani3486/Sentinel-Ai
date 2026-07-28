"use client";

/**
 * Sentinel AI — Login Form Component
 *
 * Simplified login form featuring:
 * - 1-Click Instant Demo Sign-In (Admin, Data Engineer, ML Engineer, Viewer)
 * - Auto-fill sample credentials button
 * - In-card Tab switcher between Sign In and Create Account
 * - Google SSO modal & standard Email/Password authentication
 */

import Link from "next/link";
import { type FormEvent, useState } from "react";
import { AlertTriangle, ArrowRight, CheckCircle2, KeyRound, Lock, Mail, Shield, Sparkles, User, Zap } from "lucide-react";

import { useAuth } from "@/hooks/use-auth";
import { UserRole } from "@/types/auth";

export function LoginForm() {
  const { login, loginWithGoogle } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [demoRoleLoading, setDemoRoleLoading] = useState<string | null>(null);

  // Google Modal State
  const [showGoogleModal, setShowGoogleModal] = useState(false);
  const [googleEmail, setGoogleEmail] = useState("");
  const [googleName, setGoogleName] = useState("");
  const [googleRole, setGoogleRole] = useState<UserRole>(UserRole.ADMIN);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  // 1-Click Demo Login handler
  const handleQuickDemoLogin = async (role: UserRole, defaultEmail: string, name: string) => {
    setError(null);
    setDemoRoleLoading(role);
    try {
      await loginWithGoogle(defaultEmail, name, role);
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const axiosErr = err as { response?: { data?: { message?: string } } };
        setError(axiosErr.response?.data?.message || "Demo login failed");
      } else {
        setError("An unexpected error occurred during demo login");
      }
    } finally {
      setDemoRoleLoading(null);
    }
  };

  const handleFillDemoCredentials = () => {
    setEmail("admin@sentinel-ai.io");
    setPassword("password123!");
    setError(null);
  };

  const handleGoogleSignIn = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsGoogleLoading(true);
    try {
      await loginWithGoogle(
        googleEmail.trim() || undefined,
        googleName.trim() || undefined,
        googleRole
      );
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const axiosErr = err as { response?: { data?: { message?: string } } };
        setError(axiosErr.response?.data?.message || "Google sign-in failed");
      } else {
        setError("An unexpected error occurred during Google sign-in");
      }
    } finally {
      setIsGoogleLoading(false);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await login({ email, password });
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const axiosErr = err as { response?: { data?: { message?: string } } };
        setError(axiosErr.response?.data?.message || "Login failed");
      } else {
        setError("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-8">
      <div className="w-full max-w-lg">
        {/* Header Logo */}
        <div className="mb-6 flex flex-col items-center animate-fade-in text-center">
          <div
            className="mb-3 flex h-14 w-14 items-center justify-center rounded-2xl"
            style={{
              background: "linear-gradient(135deg, var(--color-sentinel-blue), var(--color-sentinel-purple))",
              boxShadow: "0 8px 32px rgba(59, 130, 246, 0.35)",
            }}
          >
            <Zap size={28} className="text-white" />
          </div>
          <h1
            className="text-2xl font-bold tracking-tight"
            style={{ color: "var(--color-sentinel-text)" }}
          >
            Sentinel AI
          </h1>
          <p
            className="mt-1 text-xs"
            style={{ color: "var(--color-sentinel-text-muted)" }}
          >
            Industrial Data Quality & AI Observability Platform
          </p>
        </div>

        {/* Auth Card Container */}
        <div className="glass-card p-6 md:p-8 animate-fade-in-delay-1 border border-white/10 shadow-2xl rounded-2xl">
          {/* Tab Switcher */}
          <div className="mb-6 flex rounded-xl bg-black/30 p-1 border border-white/5">
            <button
              type="button"
              className="flex-1 py-2 text-center text-xs font-semibold rounded-lg transition-all shadow-sm bg-gradient-to-r from-blue-600 to-indigo-600 text-white"
            >
              Sign In
            </button>
            <Link
              href="/register"
              className="flex-1 py-2 text-center text-xs font-medium rounded-lg transition-all text-gray-400 hover:text-white hover:bg-white/5"
            >
              Create Account
            </Link>
          </div>

          {/* 1-Click Instant Demo Login Banner */}
          <div className="mb-6 rounded-xl border border-blue-500/30 bg-blue-500/10 p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="flex items-center gap-1.5 text-xs font-bold text-blue-400 uppercase tracking-wider">
                <Sparkles size={14} className="text-blue-400" />
                1-Click Instant Access
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-300 font-medium">
                No password required
              </span>
            </div>
            <p className="text-xs text-gray-300 mb-3">
              Instantly explore the platform with a demo persona:
            </p>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                disabled={Boolean(demoRoleLoading || isLoading)}
                onClick={() => handleQuickDemoLogin(UserRole.ADMIN, "demo.admin@sentinel-ai.io", "Demo Admin")}
                className="flex items-center justify-center gap-2 py-2 px-3 rounded-lg border border-blue-500/20 bg-blue-900/30 hover:bg-blue-600/30 text-xs font-medium text-blue-200 transition-all active:scale-[0.98] disabled:opacity-50"
              >
                {demoRoleLoading === UserRole.ADMIN ? (
                  <div className="spinner" />
                ) : (
                  <>
                    <Shield size={13} className="text-blue-400" />
                    Admin
                  </>
                )}
              </button>

              <button
                type="button"
                disabled={Boolean(demoRoleLoading || isLoading)}
                onClick={() => handleQuickDemoLogin(UserRole.DATA_ENGINEER, "demo.engineer@sentinel-ai.io", "Data Engineer")}
                className="flex items-center justify-center gap-2 py-2 px-3 rounded-lg border border-purple-500/20 bg-purple-900/30 hover:bg-purple-600/30 text-xs font-medium text-purple-200 transition-all active:scale-[0.98] disabled:opacity-50"
              >
                {demoRoleLoading === UserRole.DATA_ENGINEER ? (
                  <div className="spinner" />
                ) : (
                  <>
                    <Zap size={13} className="text-purple-400" />
                    Data Engineer
                  </>
                )}
              </button>

              <button
                type="button"
                disabled={Boolean(demoRoleLoading || isLoading)}
                onClick={() => handleQuickDemoLogin(UserRole.ML_ENGINEER, "demo.ml@sentinel-ai.io", "ML Engineer")}
                className="flex items-center justify-center gap-2 py-2 px-3 rounded-lg border border-emerald-500/20 bg-emerald-900/30 hover:bg-emerald-600/30 text-xs font-medium text-emerald-200 transition-all active:scale-[0.98] disabled:opacity-50"
              >
                {demoRoleLoading === UserRole.ML_ENGINEER ? (
                  <div className="spinner" />
                ) : (
                  <>
                    <KeyRound size={13} className="text-emerald-400" />
                    ML Engineer
                  </>
                )}
              </button>

              <button
                type="button"
                disabled={Boolean(demoRoleLoading || isLoading)}
                onClick={() => handleQuickDemoLogin(UserRole.VIEWER, "demo.viewer@sentinel-ai.io", "Demo Viewer")}
                className="flex items-center justify-center gap-2 py-2 px-3 rounded-lg border border-gray-500/20 bg-gray-800/40 hover:bg-gray-700/40 text-xs font-medium text-gray-300 transition-all active:scale-[0.98] disabled:opacity-50"
              >
                {demoRoleLoading === UserRole.VIEWER ? (
                  <div className="spinner" />
                ) : (
                  <>
                    <User size={13} className="text-gray-400" />
                    Viewer
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Divider */}
          <div className="relative mb-6 flex items-center justify-center">
            <div className="absolute inset-0 flex items-center" aria-hidden="true">
              <div
                className="w-full border-t"
                style={{ borderColor: "var(--color-sentinel-border-subtle)" }}
              />
            </div>
            <div
              className="relative px-3 text-[11px] uppercase tracking-wider"
              style={{
                background: "var(--color-sentinel-surface-card)",
                color: "var(--color-sentinel-text-muted)",
              }}
            >
              Or Sign In With Email / SSO
            </div>
          </div>

          {/* Google Sign-In Button */}
          <button
            type="button"
            disabled={isGoogleLoading || isLoading || Boolean(demoRoleLoading)}
            onClick={() => setShowGoogleModal(true)}
            className="mb-4 flex w-full items-center justify-center gap-3 rounded-xl border py-2.5 px-4 text-xs font-medium transition-all shadow-sm hover:bg-white/5 active:scale-[0.99]"
            style={{
              borderColor: "var(--color-sentinel-border)",
              background: "rgba(255, 255, 255, 0.03)",
              color: "var(--color-sentinel-text)",
            }}
          >
            {isGoogleLoading ? (
              <div className="spinner" />
            ) : (
              <>
                <svg className="h-4 w-4" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                  />
                </svg>
                Continue with Google Single Sign-On
              </>
            )}
          </button>

          {error && (
            <div
              className="mb-4 flex items-center gap-2 rounded-lg px-4 py-3 text-xs"
              style={{
                background: "rgba(239, 68, 68, 0.1)",
                border: "1px solid rgba(239, 68, 68, 0.2)",
                color: "var(--color-sentinel-red)",
              }}
            >
              <AlertTriangle size={15} />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label
                  htmlFor="login-email"
                  className="text-xs font-medium"
                  style={{ color: "var(--color-sentinel-text-secondary)" }}
                >
                  Email address
                </label>
                <button
                  type="button"
                  onClick={handleFillDemoCredentials}
                  className="text-[11px] text-blue-400 hover:text-blue-300 underline font-medium flex items-center gap-1"
                >
                  <CheckCircle2 size={12} /> Auto-fill credentials
                </button>
              </div>
              <div className="relative">
                <Mail
                  size={15}
                  className="absolute left-3 top-1/2 -translate-y-1/2"
                  style={{ color: "var(--color-sentinel-text-muted)" }}
                />
                <input
                  id="login-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="admin@sentinel-ai.io"
                  required
                  className="input-sentinel pl-9 text-xs"
                  autoComplete="email"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="login-password"
                className="mb-1 block text-xs font-medium"
                style={{ color: "var(--color-sentinel-text-secondary)" }}
              >
                Password
              </label>
              <div className="relative">
                <Lock
                  size={15}
                  className="absolute left-3 top-1/2 -translate-y-1/2"
                  style={{ color: "var(--color-sentinel-text-muted)" }}
                />
                <input
                  id="login-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter password"
                  required
                  minLength={8}
                  className="input-sentinel pl-9 text-xs"
                  autoComplete="current-password"
                />
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading || Boolean(demoRoleLoading)}
              className="btn-primary w-full text-xs font-semibold"
              style={{ height: "42px" }}
            >
              {isLoading ? (
                <div className="spinner" />
              ) : (
                <>
                  Sign in to Account
                  <ArrowRight size={15} />
                </>
              )}
            </button>
          </form>

          {/* Register Link Footer */}
          <p
            className="mt-5 text-center text-xs"
            style={{ color: "var(--color-sentinel-text-secondary)" }}
          >
            Don&apos;t have an account yet?{" "}
            <Link
              href="/register"
              className="font-medium text-blue-400 hover:text-blue-300 transition-colors underline"
            >
              Create account now
            </Link>
          </p>
        </div>

        {/* Google SSO Modal */}
        {showGoogleModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
            <div
              className="w-full max-w-md rounded-2xl p-6 shadow-2xl border transition-all"
              style={{
                background: "var(--color-sentinel-surface-card)",
                borderColor: "var(--color-sentinel-border)",
              }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <svg className="h-5 w-5" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                    />
                  </svg>
                  <h3 className="text-base font-bold" style={{ color: "var(--color-sentinel-text)" }}>
                    Google Single Sign-On
                  </h3>
                </div>
                <button
                  type="button"
                  onClick={() => setShowGoogleModal(false)}
                  className="text-xs px-2.5 py-1 rounded bg-white/10 text-gray-400 hover:text-white transition-colors"
                >
                  Close
                </button>
              </div>

              <p className="text-xs mb-4 text-gray-400">
                Choose your email address and platform role to sign in instantly:
              </p>

              <form onSubmit={handleGoogleSignIn} className="space-y-3.5">
                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-300">
                    Google Email
                  </label>
                  <div className="relative">
                    <Mail size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      type="email"
                      required
                      value={googleEmail}
                      onChange={(e) => setGoogleEmail(e.target.value)}
                      placeholder="user@gmail.com"
                      className="input-sentinel pl-9 text-xs"
                    />
                  </div>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-300">
                    Full Name
                  </label>
                  <div className="relative">
                    <User size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      required
                      value={googleName}
                      onChange={(e) => setGoogleName(e.target.value)}
                      placeholder="Jane Smith"
                      className="input-sentinel pl-9 text-xs"
                    />
                  </div>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-300">
                    Assign Role
                  </label>
                  <div className="relative">
                    <Shield size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <select
                      value={googleRole}
                      onChange={(e) => setGoogleRole(e.target.value as UserRole)}
                      className="input-sentinel pl-9 text-xs cursor-pointer"
                      style={{ colorScheme: "dark" }}
                    >
                      <option value={UserRole.ADMIN}>Administrator (Full Access)</option>
                      <option value={UserRole.DATA_ENGINEER}>Data Engineer (Pipelines)</option>
                      <option value={UserRole.ML_ENGINEER}>ML Engineer (Analytics)</option>
                      <option value={UserRole.VIEWER}>Viewer (Read-Only)</option>
                    </select>
                  </div>
                </div>

                <div className="pt-2 flex gap-2">
                  <button
                    type="button"
                    onClick={() => setShowGoogleModal(false)}
                    className="w-1/3 py-2 rounded-xl border border-gray-700 text-xs font-medium text-gray-300 hover:bg-white/5"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isGoogleLoading}
                    className="w-2/3 py-2 rounded-xl text-xs font-semibold text-white transition-all shadow-md flex items-center justify-center gap-2 hover:brightness-110"
                    style={{
                      background: "linear-gradient(135deg, var(--color-sentinel-blue), var(--color-sentinel-purple))",
                    }}
                  >
                    {isGoogleLoading ? <div className="spinner" /> : <>Continue <ArrowRight size={14} /></>}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Footer */}
        <p
          className="mt-6 text-center text-xs animate-fade-in-delay-2"
          style={{ color: "var(--color-sentinel-text-muted)" }}
        >
          Sentinel AI — Enterprise Data Quality Platform
        </p>
      </div>
    </div>
  );
}
