/**
 * Sentinel AI — Authentication Types
 *
 * Shared type definitions for all auth-related data flows:
 * login, registration, token management, and user context.
 */

export enum UserRole {
  ADMIN = "admin",
  DATA_ENGINEER = "data_engineer",
  ML_ENGINEER = "ml_engineer",
  VIEWER = "viewer",
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_superuser: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  role?: UserRole | string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
