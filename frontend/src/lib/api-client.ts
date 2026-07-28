/**
 * Sentinel AI — API Client
 *
 * Axios instance with interceptors for:
 * - Automatic Bearer token injection
 * - Token refresh on 401 responses
 * - Standardized error handling
 */

import axios, {
  type AxiosError,
  type AxiosInstance,
  type InternalAxiosRequestConfig,
} from "axios";

import {
  clearTokens,
  getAccessToken,
  setAccessToken,
} from "@/lib/auth";
import type { TokenResponse } from "@/types/auth";

const getBaseUrl = (): string => {
  const rawUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const trimmed = rawUrl.replace(/\/+$/, "");
  if (trimmed.endsWith("/api/v1")) {
    return trimmed;
  }
  return `${trimmed}/api/v1`;
};

const API_BASE_URL = getBaseUrl();

const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
  withCredentials: true, // Crucial: enables cross-origin cookie transmission
});

// ── Request Interceptor: Attach access token ────────────────────────────────

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response Interceptor: Handle 401 + auto-refresh ─────────────────────────

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null = null) {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else if (token) {
      promise.resolve(token);
    }
  });
  failedQueue = [];
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    if (!originalRequest || !error.response) {
      return Promise.reject(error);
    }

    // Don't retry auth endpoints
    if (
      error.response.status === 401 &&
      !originalRequest.url?.includes("/auth/login") &&
      !originalRequest.url?.includes("/auth/refresh") &&
      !(originalRequest as unknown as Record<string, boolean>)._retry
    ) {
      if (isRefreshing) {
        // Queue the request while refresh is in progress
        return new Promise<string>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return apiClient(originalRequest);
        });
      }

      (originalRequest as unknown as Record<string, boolean>)._retry = true;
      isRefreshing = true;

      try {
        // Post to refresh without body. Cookie is transmitted automatically.
        const { data } = await axios.post<TokenResponse>(
          `${API_BASE_URL}/auth/refresh`,
          {},
          { withCredentials: true }
        );

        setAccessToken(data.access_token);
        processQueue(null, data.access_token);

        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        clearTokens();
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
