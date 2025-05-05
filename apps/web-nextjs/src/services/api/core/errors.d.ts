/**
 * Type declarations for custom error types
 */

export declare class APIError extends Error {
  constructor(message: string);
}

export declare class NetworkError extends Error {
  constructor(message: string);
}

export declare class ValidationError extends Error {
  constructor(message: string);
}

export declare class AuthError extends Error {
  constructor(message: string);
}

export declare class CacheHitError extends Error {
  data: unknown;
  constructor(data: unknown);
}
