import axios, { AxiosRequestConfig, AxiosResponse } from "axios";
import {
  APIError,
  NetworkError,
  ValidationError,
  AuthError,
  CacheHitError,
} from "./errors";

// Import config properly with ES modules
import defaultConfig from "../../../config";
import { createLogger } from "@/utils/logging";

// Create dedicated logger for API client
const logger = createLogger("APIClient");

// Use proper typing and fallback
let config: typeof defaultConfig;
try {
  config = defaultConfig;
} catch {
  // Fallback config if import fails
  logger.warn("Failed to load config, using fallback values");
  config = {
    api: {
      timeout: 10000, // 10 seconds
      bffUrl: process.env.NEXT_PUBLIC_BFF_API_URL || "http://localhost:8001",
    },
    auth: {
      tokenKey: "auth_token",
    },
  } as typeof defaultConfig;
}

// Production validation
if (
  typeof window !== "undefined" &&
  process.env.NODE_ENV === "production" &&
  !process.env.NEXT_PUBLIC_BFF_API_URL
) {
  logger.error(
    "NEXT_PUBLIC_BFF_API_URL must be set in production environment"
  );
}

// API configuration - always use environment variables or config
export const API_CONFIG = {
  baseUrl:
    config.api.bffUrl ||
    process.env.NEXT_PUBLIC_BFF_API_URL ||
    "http://localhost:8001",
  timeout: config.api.timeout || 10000,
};

// Create API client instance with retry config
const apiClient = axios.create({
  baseURL: API_CONFIG.baseUrl,
  timeout: API_CONFIG.timeout,
  headers: {
    "Content-Type": "application/json",
  },
});

logger.info("API client initialized", {
  baseURL: apiClient.defaults.baseURL,
  timeout: apiClient.defaults.timeout,
});

// Request cache
const requestCache = new Map<string, { data: unknown; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

// Event for token expiration
const tokenExpiredEvent = new CustomEvent("auth:token-expired");

// Add a request interceptor to handle authentication and caching
apiClient.interceptors.request.use(
  (axiosConfig) => {
    // Log outgoing requests
    logger.debug(
      `Request: ${axiosConfig.method?.toUpperCase()} ${axiosConfig.url}`,
      {
        params: axiosConfig.params,
        headers: axiosConfig.headers,
      }
    );

    // Only try to get token in browser environment
    if (typeof window !== "undefined") {
      try {
        const token = localStorage.getItem(config.auth.tokenKey);
        if (token && axiosConfig.headers) {
          axiosConfig.headers.Authorization = `Bearer ${token}`;
          logger.debug("Added auth token to request");
        }
      } catch (e) {
        // Ignore localStorage errors during SSR
        logger.warn("Failed to access localStorage:", e);
      }
    }

    // Check cache for GET requests
    if (axiosConfig.method === "get") {
      const cacheKey = `${axiosConfig.url}${JSON.stringify(
        axiosConfig.params || {}
      )}`;
      const cachedResponse = requestCache.get(cacheKey);

      if (cachedResponse && Date.now() - cachedResponse.timestamp < CACHE_TTL) {
        logger.debug(`Cache hit for ${axiosConfig.url}`, {
          age: Date.now() - cachedResponse.timestamp,
        });
        throw new CacheHitError(cachedResponse.data);
      }
    }

    return axiosConfig;
  },
  (error) => {
    logger.error("Request interceptor error:", error);
    return Promise.reject(error);
  }
);

// Add a response interceptor for error handling and caching
apiClient.interceptors.response.use(
  (response) => {
    // Log successful responses
    logger.debug(
      `Response: ${response.status} ${response.config.method?.toUpperCase()} ${
        response.config.url
      }`
    );

    // Cache successful GET responses
    if (response.config.method === "get") {
      const cacheKey = `${response.config.url}${JSON.stringify(
        response.config.params || {}
      )}`;
      requestCache.set(cacheKey, {
        data: response.data,
        timestamp: Date.now(),
      });
      logger.debug(`Cached response for ${response.config.url}`);
    }
    return response;
  },
  (error: unknown) => {
    // Handle cache hits
    if (error instanceof CacheHitError) {
      const cacheError = error as CacheHitError;
      return Promise.resolve({ data: cacheError.data } as AxiosResponse);
    }

    // Type guard to ensure we're handling AxiosError
    if (axios.isAxiosError(error)) {
      // Log error details
      const requestInfo = {
        method: error.config?.method?.toUpperCase(),
        url: error.config?.url,
        status: error.response?.status,
      };

      logger.error(`API error: ${requestInfo.method} ${requestInfo.url}`, {
        status: requestInfo.status,
        data: error.response?.data,
      });

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
              logger.warn("Token expired or invalid, clearing local storage");
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
          throw new APIError("Resource not found", 404);
        case 409:
          // For collection endpoints, 409 often means the item is already in the desired state
          // Check if this is a collection operation (like/watchlist/watched)
          if (
            error.config?.url?.includes("/liked-movies") ||
            error.config?.url?.includes("/watchlist") ||
            error.config?.url?.includes("/watched-movies")
          ) {
            logger.info(
              `409 Conflict treated as success for ${error.config.url}: ${message}`
            );

            // Return a successful response with the appropriate data structure
            // This prevents the UI from showing an error when the operation is essentially successful
            return Promise.resolve({
              data: {
                success: true,
                message: message || "Operation already completed",
                movie_id: parseInt(
                  error.config.url.split("/").pop() || "0",
                  10
                ),
              },
            } as AxiosResponse);
          }
          // For other endpoints, treat 409 as a regular error
          throw new APIError(message);
        case 429:
          throw new APIError("Too many requests", 429);
        default:
          throw new APIError(message, status);
      }
    }

    // If not an Axios error, re-throw
    logger.error("Unhandled API error:", error);
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
    logger.debug(`Fetching data from ${endpoint}`, { retries });
    const response = await apiClient.get<T>(endpoint, config);
    return response.data;
  } catch (error) {
    if (retries > 0 && error instanceof NetworkError) {
      logger.warn(
        `Network error fetching ${endpoint}, retrying (${retries} attempts left)`
      );
      await new Promise((resolve) => setTimeout(resolve, 1000));
      return fetchData<T>(endpoint, config, retries - 1);
    }
    logger.error(`Failed to fetch data from ${endpoint}`, { error });
    throw error;
  }
};

// Generic post function
export const postData = async <T>(
  endpoint: string,
  data: unknown,
  config?: AxiosRequestConfig
): Promise<T> => {
  try {
    logger.debug(`Posting data to ${endpoint}`);
    const response = await apiClient.post<T>(endpoint, data, config);
    return response.data;
  } catch (error) {
    logger.error(`Failed to post data to ${endpoint}`, { error });
    throw error;
  }
};

// Generic put function
export const putData = async <T>(
  endpoint: string,
  data: unknown,
  config?: AxiosRequestConfig
): Promise<T> => {
  try {
    logger.debug(`Putting data to ${endpoint}`);
    const response = await apiClient.put<T>(endpoint, data, config);
    return response.data;
  } catch (error) {
    logger.error(`Failed to put data to ${endpoint}`, { error });
    throw error;
  }
};

// Generic delete function
export const deleteData = async <T>(
  endpoint: string,
  config?: AxiosRequestConfig
): Promise<T> => {
  try {
    logger.debug(`Deleting data from ${endpoint}`);
    const response = await apiClient.delete<T>(endpoint, config);
    return response.data;
  } catch (error) {
    logger.error(`Failed to delete data from ${endpoint}`, { error });
    throw error;
  }
};

// Function for uploading form data
export const uploadFormData = async <T>(
  endpoint: string,
  formData: FormData,
  config?: AxiosRequestConfig
): Promise<T> => {
  try {
    logger.debug(`Uploading form data to ${endpoint}`);
    const mergedConfig: AxiosRequestConfig = {
      ...config,
      headers: {
        ...config?.headers,
        "Content-Type": "multipart/form-data",
      },
    };

    const response = await apiClient.post<T>(endpoint, formData, mergedConfig);
    return response.data;
  } catch (error) {
    logger.error(`Failed to upload form data to ${endpoint}`, { error });
    throw error;
  }
};

/**
 * Generic API client class for entity-based operations
 * This provides a consistent interface for CRUD operations on entities
 */
export class APIClient<T> {
  protected endpoint: string;
  protected logger: ReturnType<typeof createLogger>;

  constructor(endpoint: string) {
    // Remove trailing slash if present
    this.endpoint = endpoint.endsWith("/") ? endpoint.slice(0, -1) : endpoint;
    // Create a logger specific to this client instance
    this.logger = createLogger(`APIClient:${this.endpoint}`);
    this.logger.debug("Initialized");
  }

  /**
   * Get all entities with optional query parameters
   */
  getAll = async (
    params?: Record<string, unknown>
  ): Promise<{ data: T[]; meta?: Record<string, unknown> }> => {
    this.logger.debug("Getting all items", { params });
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
    this.logger.debug(`Getting item by ID: ${id}`);
    return fetchData<T>(`${this.endpoint}/${id}`);
  };

  /**
   * Create a new entity
   */
  create = async (data: Partial<T>): Promise<T> => {
    this.logger.debug("Creating new item", { data });
    return postData<T>(this.endpoint, data);
  };

  /**
   * Update an existing entity
   */
  update = async (id: number | string, data: Partial<T>): Promise<T> => {
    this.logger.debug(`Updating item ${id}`, { data });
    return putData<T>(`${this.endpoint}/${id}`, data);
  };

  /**
   * Delete an entity
   */
  delete = async (id: number | string): Promise<void> => {
    this.logger.debug(`Deleting item ${id}`);
    return deleteData<void>(`${this.endpoint}/${id}`);
  };

  /**
   * Execute a custom query against the API
   */
  query = async <R = T>(
    queryString: string,
    config?: AxiosRequestConfig
  ): Promise<R> => {
    this.logger.debug(`Executing custom query: ${queryString}`, { config });
    // Add a slash if queryString doesn't start with one, isn't empty, and doesn't start with ?
    const separator =
      queryString &&
      !queryString.startsWith("/") &&
      !queryString.startsWith("?")
        ? "/"
        : "";
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
    this.logger.debug(`Uploading form to ${path}`);
    const fullPath = path.startsWith("/") ? path : `${this.endpoint}/${path}`;
    return uploadFormData<R>(fullPath, formData, config);
  };
}

// For backward compatibility, expose same function names used in BFF client
export const bffFetchData = fetchData;
export const bffPostData = postData;
export const bffPutData = putData;
export const bffDeleteData = deleteData;
export const bffUploadFormData = uploadFormData;

// For backward compatibility, create a BFF client creator that just uses the standard client
export const createBFFClient = <T>(endpoint: string): APIClient<T> => {
  return new APIClient<T>(endpoint);
};

// Check token validity
export const isTokenValid = (): boolean => {
  if (typeof window === "undefined") return false;

  try {
    const token = localStorage.getItem(config.auth.tokenKey);
    if (!token) {
      logger.debug("No token found in localStorage");
      return false;
    }

    // Simple check based on token format (JWT)
    if (token.split(".").length !== 3) {
      logger.warn("Invalid token format found in localStorage");
      return false;
    }

    logger.debug("Token validation passed");
    return true;
  } catch (e) {
    logger.error("Error checking token validity:", e);
    return false;
  }
};

// Export apiClient as default and also as a named export
export default apiClient;
export { apiClient };
