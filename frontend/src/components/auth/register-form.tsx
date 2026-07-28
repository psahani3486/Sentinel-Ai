"use client";

/**
 * Sentinel AI — Registration Form Component
 *
 * Simplified registration form with:
 * - 1-Click Instant Demo Account Creation
 * - Visual Role Selection cards
 * - Auto-fill sample user details
 * - Unified Card Tab switcher (Sign In | Create Account)
 * - Google SSO and standard Email registration
 */

import Link from "next/link";
import { type FormEvent, useState } from "react";
import { AlertTriangle, ArrowRight, CheckCircle2, KeyRound, Lock, Mail, Shield, Sparkles, User, Zap } from "lucide-react";

import { useAuth } from "@/hooks/use-auth";
import { UserRole } from "@/types/auth";

export function RegisterForm() {
  const { register, loginWithGoogle } = useAuth();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>(UserRole.ADMIN);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [demoRoleLoading, setDemoRoleLoading] = useState<string | null>(null);

  // Google Modal State
  const [showGoogleModal, setShowGoogleModal] = useState(false);
  const [googleEmail, setGoogleEmail] = useState("");
  const [googleName, setGoogleName] = useState("");
  const [googleRole, setGoogleRole] = useState<UserRole>(UserRole.ADMIN);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  // 1-Click Quick Registration & Sign In
  const handleQuickDemoRegister = async (selectedRole: UserRole, defaultEmail: string, name: string) => {
    setError(null);
    setDemoRoleLoading(selectedRole);
    try {
      await loginWithGoogle(defaultEmail, name, selectedRole);
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const axiosErr = err as { response?: { data?: { message?: string } } };
        setError(axiosErr.response?.data?.message || "Quick registration failed");
      } else {
        setError("An unexpected error occurred during quick registration");
      }
    } finally {
      setDemoRoleLoading(null);
    }
  };

  const handleFillSampleUser = () => {
    const randomId = Math.floor(Math.random() * 899) + 100;
    setFullName(`Demo Engineer ${randomId}`);
    setEmail(`engineer${randomId}@sentinel-ai.io`);
    setPassword("SentinelSecurePass123!");
    setError(null);
  };

  const handleGoogleSignUp = async (e: FormEvent) => {
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
        setError(axiosErr.response?.data?.message || "Google sign-up failed");
      } else {
        setError("An unexpected error occurred during Google sign-up");
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
      await register({ email, password, full_name: fullName, role });
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const axiosErr = err as { response?: { data?: { message?: string } } };
        setError(axiosErr.response?.data?.message || "Registration failed");
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
            Create Sentinel AI Account
          </h1>
          <p
            className="mt-1 text-xs"
            style={{ color: "var(--color-sentinel-text-muted)" }}
          >
            Get started with real-time industrial data observability
          </p>
        </div>

        {/* Form Card */}
        <div className="glass-card p-6 md:p-8 animate-fade-in-delay-1 border border-white/10 shadow-2xl rounded-2xl">
          {/* Tab Switcher */}
          <div className="mb-6 flex rounded-xl bg-black/30 p-1 border border-white/5">
            <Link
              href="/login"
              className="flex-1 py-2 text-center text-xs font-medium rounded-lg transition-all text-gray-400 hover:text-white hover:bg-white/5"
            >
              Sign In
            </Link>
            <button
              type="button"
              className="flex-1 py-2 text-center text-xs font-semibold rounded-lg transition-all shadow-sm bg-gradient-to-r from-blue-600 to-indigo-600 text-white"
            >
              Create Account
            </button>
          </div>

          {/* 1-Click Quick Register Banner */}
          <div className="mb-6 rounded-xl border border-indigo-500/30 bg-indigo-500/10 p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="flex items-center gap-1.5 text-xs font-bold text-indigo-400 uppercase tracking-wider">
                <Sparkles size={14} className="text-indigo-400" />
                1-Click Quick Signup
              </span>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-medium">
                Instant trial access
              </span>
            </div>
            <p className="text-xs text-gray-300 mb-3">
              Create an instant demo profile with pre-configured access:
            </p>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                disabled={Boolean(demoRoleLoading || isLoading)}
                onClick={() => handleQuickDemoRegister(UserRole.ADMIN, "new.admin@sentinel-ai.io", "New Admin")}
                className="flex items-center justify-center gap-2 py-2 px-3 rounded-lg border border-blue-500/20 bg-blue-900/30 hover:bg-blue-600/30 text-xs font-medium text-blue-200 transition-all active:scale-[0.98] disabled:opacity-50"
              >
                {demoRoleLoading === UserRole.ADMIN ? (
                  <div className="spinner" />
                ) : (
                  <>
                    <Shield size={13} className="text-blue-400" />
                    Admin Account
                  </>
                )}
              </button>

              <button
                type="button"
                disabled={Boolean(demoRoleLoading || isLoading)}
                onClick={() => handleQuickDemoRegister(UserRole.DATA_ENGINEER, "new.engineer@sentinel-ai.io", "New Engineer")}
                className="flex items-center justify-center gap-2 py-2 px-3 rounded-lg border border-purple-500/20 bg-purple-900/30 hover:bg-purple-600/30 text-xs font-medium text-purple-200 transition-all active:scale-[0.98] disabled:opacity-50"
              >
                {demoRoleLoading === UserRole.DATA_ENGINEER ? (
                  <div className="spinner" />
                ) : (
                  <>
                    <Zap size={13} className="text-purple-400" />
                    Engineer Account
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
              Or Register Custom Profile
            </div>
          </div>

          {/* Google Sign-Up Button */}
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
                Sign up with Google Single Sign-On
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
            {/* Full Name */}
            <div>
              <div className="flex justify-between items-center mb-1">
                <label
                  htmlFor="register-name"
                  className="text-xs font-medium"
                  style={{ color: "var(--color-sentinel-text-secondary)" }}
                >
                  Full name
                </label>
                <button
                  type="button"
                  onClick={handleFillSampleUser}
                  className="text-[11px] text-blue-400 hover:text-blue-300 underline font-medium flex items-center gap-1"
                >
                  <CheckCircle2 size={12} /> Auto-fill details
                </button>
              </div>
              <div className="relative">
                <User
                  size={15}
                  className="absolute left-3 top-1/2 -translate-y-1/2"
                  style={{ color: "var(--color-sentinel-text-muted)" }}
                />
                <input
                  id="register-name"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Jane Smith"
                  required
                  className="input-sentinel pl-9 text-xs"
                  autoComplete="name"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label
                htmlFor="register-email"
                className="mb-1 block text-xs font-medium"
                style={{ color: "var(--color-sentinel-text-secondary)" }}
              >
                Email address
              </label>
              <div className="relative">
                <Mail
                  size={15}
                  className="absolute left-3 top-1/2 -translate-y-1/2"
                  style={{ color: "var(--color-sentinel-text-muted)" }}
                />
                <input
                  id="register-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="engineer@company.com"
                  required
                  className="input-sentinel pl-9 text-xs"
                  autoComplete="email"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="register-password"
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
                  id="register-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 8 characters"
                  required
                  minLength={8}
                  className="input-sentinel pl-9 text-xs"
                  autoComplete="new-password"
                />
              </div>
            </div>

            {/* Visual Role Selection */}
            <div>
              <label className="mb-1.5 block text-xs font-medium text-gray-300">
                Platform Role
              </label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { r: UserRole.ADMIN, label: "Administrator", desc: "Full system access & user management", icon: Shield },
                  { r: UserRole.DATA_ENGINEER, label: "Data Engineer", desc: "Pipelines, drift & telemetry", icon: Zap },
                  { r: UserRole.ML_ENGINEER, label: "ML Engineer", desc: "Forecasting & anomaly models", icon: KeyRound },
                  { r: UserRole.VIEWER, label: "Viewer", desc: "Read-only dashboards & alerts", icon: User },
                ].map((item) => {
                  const IconComp = item.icon;
                  const isSelected = role === item.r;
                  return (
                    <button
                      key={item.r}
                      type="button"
                      onClick={() => setRole(item.r)}
                      className={`p-2.5 rounded-xl border text-left transition-all text-xs flex flex-col justify-between ${
                        isSelected
                          ? "border-blue-500 bg-blue-500/15 ring-1 ring-blue-500"
                          : "border-gray-700/60 bg-white/5 hover:border-gray-600"
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-semibold text-white flex items-center gap-1.5">
                          <IconComp size={13} className={isSelected ? "text-blue-400" : "text-gray-400"} />
                          {item.label}
                        </span>
                        {isSelected && <CheckCircle2 size={13} className="text-blue-400" />}
                      </div>
                      <span className="text-[10px] text-gray-400 leading-tight">
                        {item.desc}
                      </span>
                    </button>
                  );
                })}
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
                  Complete Registration & Sign In
                  <ArrowRight size={15} />
                </>
              )}
            </button>
          </form>

          {/* Already registered Footer */}
          <p
            className="mt-5 text-center text-xs"
            style={{ color: "var(--color-sentinel-text-secondary)" }}
          >
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-medium text-blue-400 hover:text-blue-300 transition-colors underline"
            >
              Sign in instead
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
                    Google Single Sign-Up
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
                Choose your email address and platform role to register instantly:
              </p>

              <form onSubmit={handleGoogleSignUp} className="space-y-3.5">
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
                    {isGoogleLoading ? <div className="spinner" /> : <>Complete Sign-Up <ArrowRight size={14} /></>}
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
