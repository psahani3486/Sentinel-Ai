import type { Metadata } from "next";
import { LoginForm } from "@/components/auth/login-form";

export const metadata: Metadata = {
  title: "Sign In — Sentinel AI",
  description: "Sign in to your Sentinel AI account",
};

export default function LoginPage() {
  return <LoginForm />;
}
