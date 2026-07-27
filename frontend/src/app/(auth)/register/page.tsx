import type { Metadata } from "next";
import { RegisterForm } from "@/components/auth/register-form";

export const metadata: Metadata = {
  title: "Create Account — Sentinel AI",
  description: "Create your Sentinel AI account",
};

export default function RegisterPage() {
  return <RegisterForm />;
}
