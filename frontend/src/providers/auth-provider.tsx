"use client";

/**
 * Sentinel AI — Auth Context Provider
 *
 * Manages authentication state across the application:
 * - Persists tokens in localStorage
 * - Auto-loads user on mount
 * - Provides login/logout/register actions
 * - Redirects on auth state changes
 */

import { useRouter } from "next/navigation";
import {
  createContext,
  type ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import apiClient from "@/lib/api-client";
import {
  clearTokens,
  getAccessToken,
  setAccessToken,
} from "@/lib/auth";
import type {
  AuthState,
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from "@/types/auth";

interface AuthContextValue {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  loginWithGoogle: (email?: string, fullName?: string, role?: UserRole) => Promise<void>;
  logout: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const router = useRouter();
  const [state, setState] = useState<Omit<AuthState, "refreshToken">>({
    user: null,
    accessToken: null,
    isAuthenticated: false,
    isLoading: true,
  });

  // Load user from existing token or refresh cookie on mount
  useEffect(() => {
    const loadUser = async () => {
      let accessToken = getAccessToken();

      if (!accessToken) {
        // Attempt to bootstrap session using HttpOnly refresh cookie
        try {
          const { data } = await apiClient.post<TokenResponse>("/auth/refresh", {});
          accessToken = data.access_token;
          setAccessToken(accessToken);
        } catch {
          setState((prev) => ({ ...prev, isLoading: false }));
          return;
        }
      }

      try {
        const { data: user } = await apiClient.get<User>("/auth/me");
        setState({
          user,
          accessToken,
          isAuthenticated: true,
          isLoading: false,
        });
      } catch {
        clearTokens();
        setState({
          user: null,
          accessToken: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    };

    loadUser();
  }, []);

  const login = useCallback(
    async (credentials: LoginRequest) => {
      const { data: tokens } = await apiClient.post<TokenResponse>(
        "/auth/login",
        credentials
      );

      setAccessToken(tokens.access_token);

      const { data: user } = await apiClient.get<User>("/auth/me");

      setState({
        user,
        accessToken: tokens.access_token,
        isAuthenticated: true,
        isLoading: false,
      });

      router.push("/dashboard");
    },
    [router]
  );

  const register = useCallback(
    async (data: RegisterRequest) => {
      await apiClient.post("/auth/register", data);

      // Auto-login after registration
      await login({ email: data.email, password: data.password });
    },
    [login]
  );

  const loginWithGoogle = useCallback(
    async (email?: string, fullName?: string, role?: UserRole) => {
      const googleEmail = email || "user@gmail.com";
      const googleName = fullName || "Google User";
      const googleRole = role || UserRole.ADMIN;
      const { data: tokens } = await apiClient.post<TokenResponse>(
        "/auth/google",
        { email: googleEmail, full_name: googleName, role: googleRole }
      );

      setAccessToken(tokens.access_token);

      const { data: user } = await apiClient.get<User>("/auth/me");

      setState({
        user,
        accessToken: tokens.access_token,
        isAuthenticated: true,
        isLoading: false,
      });

      router.push("/dashboard");
    },
    [router]
  );

  const logout = useCallback(async () => {
    try {
      await apiClient.post("/auth/logout");
    } catch {
      // Ignore network errors during logout
    }
    clearTokens();
    setState({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: false,
    });
    router.push("/login");
  }, [router]);

  const value = useMemo(
    () => ({
      ...state,
      login,
      register,
      loginWithGoogle,
      logout,
    }),
    [state, login, register, loginWithGoogle, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
