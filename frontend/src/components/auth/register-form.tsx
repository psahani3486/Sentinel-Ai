"use client";

/**
 * Sentinel AI — Registration Form Component
 *
 * Enterprise registration form with:
 * - Full name, email, and password fields
 * - Form validation
 * - Loading state
 * - Error display
 * - Link to login
 */

import Link from "next/link";
import { type FormEvent, useState } from "react";
import { AlertTriangle, ArrowRight, CheckCircle2, Lock, Mail, Shield, User, Zap } from "lucide-react";

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

  // Google Modal State
  const [showGoogleModal, setShowGoogleModal] = useState(false);
  const [googleEmail, setGoogleEmail] = useState("");
  const [googleName, setGoogleName] = useState("");
  const [googleRole, setGoogleRole] = useState<UserRole>(UserRole.ADMIN);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

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
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="mb-8 flex flex-col items-center animate-fade-in">
          <div
            className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl"
            style={{
              background: "linear-gradient(135deg, var(--color-sentinel-blue), var(--color-sentinel-purple))",
              boxShadow: "0 8px 32px rgba(59, 130, 246, 0.3)",
            }}
          >
            <Zap size={28} className="text-white" />
          </div>
          <h1
            className="text-2xl font-bold"
            style={{ color: "var(--color-sentinel-text)" }}
          >
            Create Account
          </h1>
          <p
            className="mt-1 text-sm"
            style={{ color: "var(--color-sentinel-text-muted)" }}
          >
            Join the Sentinel AI platform
          </p>
        </div>

        {/* Form Card */}
        <div className="glass-card p-8 animate-fade-in-delay-1">
          <h2
            className="mb-1 text-lg font-semibold"
            style={{ color: "var(--color-sentinel-text)" }}
          >
            Get started
          </h2>
          <p
            className="mb-6 text-sm"
            style={{ color: "var(--color-sentinel-text-secondary)" }}
          >
            Create your account to access the platform
          </p>

          {/* Google Sign-Up Button */}
          <button
            type="button"
            disabled={isGoogleLoading || isLoading}
            onClick={() => setShowGoogleModal(true)}
            className="mb-6 flex w-full items-center justify-center gap-3 rounded-xl border py-3 px-4 text-sm font-medium transition-all shadow-sm hover:bg-white/5 active:scale-[0.99]"
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
                Sign up with Google
              </>
            )}
          </button>

          {/* Divider */}
          <div className="relative mb-6 flex items-center justify-center">
            <div
              className="absolute inset-0 flex items-center"
              aria-hidden="true"
            >
              <div
                className="w-full border-t"
                style={{ borderColor: "var(--color-sentinel-border-subtle)" }}
              />
            </div>
            <div
              className="relative px-3 text-xs uppercase"
              style={{
                background: "var(--color-sentinel-surface-card)",
                color: "var(--color-sentinel-text-muted)",
              }}
            >
              Or register with email
            </div>
          </div>

          {error && (
            <div
              className="mb-4 flex items-center gap-2 rounded-lg px-4 py-3 text-sm"
              style={{
                background: "rgba(239, 68, 68, 0.1)",
                border: "1px solid rgba(239, 68, 68, 0.2)",
                color: "var(--color-sentinel-red)",
              }}
            >
              <AlertTriangle size={16} />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name */}
            <div>
              <label
                htmlFor="register-name"
                className="mb-1.5 block text-sm font-medium"
                style={{ color: "var(--color-sentinel-text-secondary)" }}
              >
                Full name
              </label>
              <div className="relative">
                <User
                  size={16}
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
                  className="input-sentinel pl-10"
                  autoComplete="name"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label
                htmlFor="register-email"
                className="mb-1.5 block text-sm font-medium"
                style={{ color: "var(--color-sentinel-text-secondary)" }}
              >
                Email address
              </label>
              <div className="relative">
                <Mail
                  size={16}
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
                  className="input-sentinel pl-10"
                  autoComplete="email"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label
                htmlFor="register-password"
                className="mb-1.5 block text-sm font-medium"
                style={{ color: "var(--color-sentinel-text-secondary)" }}
              >
                Password
              </label>
              <div className="relative">
                <Lock
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2"
                  style={{ color: "var(--color-sentinel-text-muted)" }}
                />
                <input
                  id="register-password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Minimum 8 characters"
                  required
                  minLength={8}
                  className="input-sentinel pl-10"
                  autoComplete="new-password"
                />
              </div>
              <p
                className="mt-1 text-xs"
                style={{ color: "var(--color-sentinel-text-muted)" }}
              >
                Must be at least 8 characters
              </p>
            </div>

            {/* Role Selection */}
            <div>
              <label
                htmlFor="register-role"
                className="mb-1.5 block text-sm font-medium"
                style={{ color: "var(--color-sentinel-text-secondary)" }}
              >
                Account Role
              </label>
              <div className="relative">
                <Shield
                  size={16}
                  className="absolute left-3 top-1/2 -translate-y-1/2"
                  style={{ color: "var(--color-sentinel-text-muted)" }}
                />
                <select
                  id="register-role"
                  value={role}
                  onChange={(e) => setRole(e.target.value as UserRole)}
                  className="input-sentinel pl-10 cursor-pointer"
                  style={{ colorScheme: "dark" }}
                >
                  <option value={UserRole.ADMIN}>Administrator (Full Access & Settings)</option>
                  <option value={UserRole.DATA_ENGINEER}>Data Engineer (Pipelines & Quality)</option>
                  <option value={UserRole.ML_ENGINEER}>ML Engineer (Models & Analytics)</option>
                  <option value={UserRole.VIEWER}>Viewer (Read-Only Dashboards)</option>
                </select>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full"
              style={{ height: "44px" }}
            >
              {isLoading ? (
                <div className="spinner" />
              ) : (
                <>
                  Create account
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          {/* Login Link */}
          <p
            className="mt-6 text-center text-sm"
            style={{ color: "var(--color-sentinel-text-secondary)" }}
          >
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-medium transition-colors"
              style={{ color: "var(--color-sentinel-blue)" }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = "var(--color-sentinel-blue-hover)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = "var(--color-sentinel-blue)";
              }}
            >
              Sign in
            </Link>
          </p>
        </div>

        {/* Google SSO Modal */}
        {showGoogleModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
            <div
              className="w-full max-w-md rounded-2xl p-6 shadow-2xl border transition-all"
              style={{
                background: "var(--color-sentinel-surface-card)",
                borderColor: "var(--color-sentinel-border)",
              }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <svg className="h-6 w-6" viewBox="0 0 24 24">
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
                  <h3 className="text-lg font-bold" style={{ color: "var(--color-sentinel-text)" }}>
                    Google Single Sign-On
                  </h3>
                </div>
                <button
                  type="button"
                  onClick={() => setShowGoogleModal(false)}
                  className="text-xs px-2 py-1 rounded bg-white/10 text-gray-400 hover:text-white"
                >
                  Close
                </button>
              </div>

              <p className="text-xs mb-4" style={{ color: "var(--color-sentinel-text-secondary)" }}>
                Enter your Gmail account details and choose your platform role to sign up via Google:
              </p>

              <form onSubmit={handleGoogleSignUp} className="space-y-4">
                <div>
                  <label className="mb-1 block text-xs font-medium text-gray-300">
                    Real Gmail Address
                  </label>
                  <div className="relative">
                    <Mail size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      type="email"
                      required
                      value={googleEmail}
                      onChange={(e) => setGoogleEmail(e.target.value)}
                      placeholder="your.email@gmail.com"
                      className="input-sentinel pl-9 text-sm"
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
                      className="input-sentinel pl-9 text-sm"
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
                      className="input-sentinel pl-9 text-sm cursor-pointer"
                      style={{ colorScheme: "dark" }}
                    >
                      <option value={UserRole.ADMIN}>Administrator (Full Access & Admin Tools)</option>
                      <option value={UserRole.DATA_ENGINEER}>Data Engineer (Pipelines & Quality)</option>
                      <option value={UserRole.ML_ENGINEER}>ML Engineer (Models & Analytics)</option>
                      <option value={UserRole.VIEWER}>Viewer (Read-Only Dashboards)</option>
                    </select>
                  </div>
                </div>

                <div className="pt-2 flex gap-2">
                  <button
                    type="button"
                    onClick={() => setShowGoogleModal(false)}
                    className="w-1/3 py-2.5 rounded-xl border border-gray-700 text-xs font-medium text-gray-300 hover:bg-white/5"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isGoogleLoading}
                    className="w-2/3 py-2.5 rounded-xl text-xs font-semibold text-white transition-all shadow-md flex items-center justify-center gap-2 hover:brightness-110"
                    style={{
                      background: "linear-gradient(135deg, var(--color-sentinel-blue), var(--color-sentinel-purple))",
                    }}
                  >
                    {isGoogleLoading ? <div className="spinner" /> : <>Complete Google Sign-Up <ArrowRight size={14} /></>}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Footer */}
        <p
          className="mt-8 text-center text-xs animate-fade-in-delay-2"
          style={{ color: "var(--color-sentinel-text-muted)" }}
        >
          Enterprise-grade Industrial IoT Platform
        </p>
      </div>
    </div>
  );
}
