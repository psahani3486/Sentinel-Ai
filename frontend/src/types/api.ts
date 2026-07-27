/**
 * Sentinel AI — Common API Types
 *
 * Shared types for pagination, error responses, and API utilities.
 */

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: unknown;
  request_id?: string;
}

export interface MessageResponse {
  message: string;
  success: boolean;
}

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
  timestamp: string;
  database?: string;
}
