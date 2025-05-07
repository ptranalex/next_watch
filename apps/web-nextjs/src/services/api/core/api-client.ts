import axios, { AxiosRequestConfig, AxiosError } from "axios";
import {
  APIError,
  NetworkError,
  ValidationError,
  AuthError,
  CacheHitError,
} from "./errors";

// Attempt to import config, if it exists at the expected path
let config: any;
try {
  config = require("../../../config").default;
} catch (e) {
  // Fallback config if import fails
  config = {
    api: {
      timeout: 10000, // 10 seconds
      baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001",
    },
    auth: {
      tokenKey: "auth_token",
    },
  };
}

// Create API client instance with retry config
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || config.api.baseUrl,
  timeout: config.api.timeout,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request cache
const requestCache = new Map<string, { data: unknown; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

// Event for token expiration
const tokenExpiredEvent = new CustomEvent("auth:token-expired");

// Add a request interceptor to handle authentication and caching
apiClient.interceptors.request.use(
  (axiosConfig) => {
    // Only try to get token in browser environment
    if (typeof window !== "undefined") {
      try {
        const token = localStorage.getItem(config.auth.tokenKey);
        if (token && axiosConfig.headers) {
          axiosConfig.headers.Authorization = `Bearer ${token}`;
        }
      } catch (e) {
        // Ignore localStorage errors during SSR
        console.warn("Failed to access localStorage:", e);
      }
    }

    // Check cache for GET requests
    if (axiosConfig.method === "get") {
      const cacheKey = `${axiosConfig.url}${JSON.stringify(
        axiosConfig.params || {}
      )}`;
      const cachedResponse = requestCache.get(cacheKey);

      if (cachedResponse && Date.now() - cachedResponse.timestamp < CACHE_TTL) {
        throw new CacheHitError(cachedResponse.data);
      }
    }

    return axiosConfig;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor for error handling and caching
apiClient.interceptors.response.use(
  (response) => {
    // Cache successful GET responses
    if (response.config.method === "get") {
      const cacheKey = `${response.config.url}${JSON.stringify(
        response.config.params || {}
      )}`;
      requestCache.set(cacheKey, {
        data: response.data,
        timestamp: Date.now(),
      });
    }
    return response;
  },
  (error: unknown) => {
    // Handle cache hits
    if (error instanceof CacheHitError) {
      const cacheError = error as CacheHitError;
      return Promise.resolve({ data: cacheError.data });
    }

    // Type guard to ensure we're handling AxiosError
    if (axios.isAxiosError(error)) {
      // Handle different types of errors
      if (!error.response) {
        throw new NetworkError("Network error occurred");
      }

      const status = error.response.status;
      const errorData = error.response.data as {
        message?: string;
        detail?: string;
      };
      const message =
        errorData?.message || errorData?.detail || "An error occurred";

      switch (status) {
        case 400:
          throw new ValidationError(message);
        case 401:
          // Clear the token on authentication failures
          if (typeof window !== "undefined") {
            // Check if the error indicates token expiration
            const isExpiredToken =
              message.includes("expired") ||
              message.includes("Invalid authentication") ||
              error.response.headers["www-authenticate"]?.includes("expired");

            if (isExpiredToken) {
              console.warn("Token expired or invalid, clearing local storage");
              // Clear token from localStorage
              localStorage.removeItem(config.auth.tokenKey);

              // Dispatch token expired event for the app to handle
              window.dispatchEvent(tokenExpiredEvent);
            }
          }
          throw new AuthError(message, true); // Pass flag indicating token issue
        case 403:
          throw new AuthError("Access denied");
        case 404:
          throw new APIError("Resource not found");
        case 429:
          throw new APIError("Too many requests");
        default:
          throw new APIError(message);
      }
    }

    // If not an Axios error, re-throw
    throw error;
  }
);

// Generic fetch function with retry logic
export const fetchData = async <T>(
  endpoint: string,
  config?: AxiosRequestConfig,
  retries = 3
): Promise<T> => {
  try {
    const response = await apiClient.get<T>(endpoint, config);
    return response.data;
  } catch (error) {
    if (retries > 0 && error instanceof NetworkError) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      return fetchData<T>(endpoint, config, retries - 1);
    }
    throw error;
  }
};

// Generic post function
export const postData = async <T>(
  endpoint: string,
  data: Record<string, unknown>,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await apiClient.post<T>(endpoint, data, config);
  return response.data;
};

// Generic put function
export const putData = async <T>(
  endpoint: string,
  data: Record<string, unknown>,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await apiClient.put<T>(endpoint, data, config);
  return response.data;
};

// Generic delete function
export const deleteData = async <T>(
  endpoint: string,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await apiClient.delete<T>(endpoint, config);
  return response.data;
};

// Function for uploading form data
export const uploadFormData = async <T>(
  endpoint: string,
  formData: FormData,
  config?: AxiosRequestConfig
): Promise<T> => {
  const mergedConfig: AxiosRequestConfig = {
    ...config,
    headers: {
      ...config?.headers,
      "Content-Type": "multipart/form-data",
    },
  };

  const response = await apiClient.post<T>(endpoint, formData, mergedConfig);
  return response.data;
};

/**
 * Generic API client class for entity-based operations
 * This provides a consistent interface for CRUD operations on entities
 */
export class APIClient<T> {
  protected endpoint: string;

  constructor(endpoint: string) {
    // Remove trailing slash if present
    this.endpoint = endpoint.endsWith("/") ? endpoint.slice(0, -1) : endpoint;
  }

  /**
   * Get all entities with optional query parameters
   */
  getAll = async (
    params?: Record<string, unknown>
  ): Promise<{ data: T[]; meta?: Record<string, unknown> }> => {
    const queryString = params
      ? `?${new URLSearchParams(this.formatParams(params)).toString()}`
      : "";
    return fetchData<{ data: T[]; meta?: Record<string, unknown> }>(
      `${this.endpoint}${queryString}`
    );
  };

  /**
   * Get a single entity by ID
   */
  getById = async (id: number | string): Promise<T> => {
    return fetchData<T>(`${this.endpoint}/${id}`);
  };

  /**
   * Create a new entity
   */
  create = async (data: Partial<T>): Promise<T> => {
    return postData<T>(this.endpoint, data);
  };

  /**
   * Update an existing entity
   */
  update = async (id: number | string, data: Partial<T>): Promise<T> => {
    return putData<T>(`${this.endpoint}/${id}`, data);
  };

  /**
   * Delete an entity
   */
  delete = async (id: number | string): Promise<void> => {
    return deleteData<void>(`${this.endpoint}/${id}`);
  };

  /**
   * Execute a custom query against the API
   */
  query = async <R = T>(
    queryString: string,
    config?: AxiosRequestConfig
  ): Promise<R> => {
    // Add a slash if queryString doesn't start with one and isn't empty
    const separator = queryString && !queryString.startsWith("/") ? "/" : "";
    return fetchData<R>(`${this.endpoint}${separator}${queryString}`, config);
  };

  /**
   * Format parameters for URL query string
   */
  protected formatParams(
    params: Record<string, unknown>
  ): Record<string, string> {
    const result: Record<string, string> = {};

    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        if (typeof value === "object") {
          result[key] = JSON.stringify(value);
        } else {
          result[key] = String(value);
        }
      }
    }

    return result;
  }

  /**
   * Upload form data to the API
   */
  uploadForm = async <R = T>(
    path: string,
    formData: FormData,
    config?: AxiosRequestConfig
  ): Promise<R> => {
    const fullPath = path.startsWith("/") ? path : `${this.endpoint}/${path}`;
    return uploadFormData<R>(fullPath, formData, config);
  };
}

// Check token validity
export const isTokenValid = (): boolean => {
  if (typeof window === "undefined") return false;

  try {
    const token = localStorage.getItem(config.auth.tokenKey);
    if (!token) return false;

    // Simple check based on token format (JWT)
    if (token.split(".").length !== 3) return false;

    return true;
  } catch (e) {
    console.error("Error checking token validity:", e);
    return false;
  }
};

// Export apiClient as default
export default apiClient;
