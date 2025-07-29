/**
 * Custom error types for API operations
 */

export class APIError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "APIError";
    this.status = status;
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "NetworkError";
  }
}

export class ValidationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ValidationError";
  }
}

export class AuthError extends Error {
  isTokenError: boolean;

  constructor(message: string, isTokenError = false) {
    super(message);
    this.name = "AuthError";
    this.isTokenError = isTokenError;
  }
}

// Custom error for cache hits
export class CacheHitError extends Error {
  data: unknown;

  constructor(data: unknown) {
    super("Cache hit");
    this.name = "CacheHitError";
    this.data = data;
  }
}
