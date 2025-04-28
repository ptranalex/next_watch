import axios, { AxiosRequestConfig } from "axios";
import config from "../config";

// Create API client instance
export const apiClient = axios.create({
  baseURL: config.api.baseUrl,
  timeout: config.api.timeout,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add a request interceptor to handle authentication
apiClient.interceptors.request.use(
  (axiosConfig) => {
    // Get the token from localStorage if we're in the browser
    if (typeof window !== "undefined") {
      const token = localStorage.getItem(config.auth.tokenKey);
      if (token && axiosConfig.headers) {
        axiosConfig.headers.Authorization = `Bearer ${token}`;
      }
    }
    return axiosConfig;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle specific error cases
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      if (error.response.status === 401) {
        // Handle unauthorized error (e.g., clear token and redirect to login)
        if (typeof window !== "undefined") {
          localStorage.removeItem(config.auth.tokenKey);
          // Could also redirect to login here
        }
      }
    }
    return Promise.reject(error);
  }
);

// Generic fetch function
export const fetchData = async <T>(
  endpoint: string,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await apiClient.get<T>(endpoint, config);
  return response.data;
};

// Generic post function
export const postData = async <T>(
  endpoint: string,
  data: any,
  config?: AxiosRequestConfig
): Promise<T> => {
  const response = await apiClient.post<T>(endpoint, data, config);
  return response.data;
};

// Generic put function
export const putData = async <T>(
  endpoint: string,
  data: any,
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

/**
 * Generic API client class for entity-based operations
 * This provides a consistent interface for CRUD operations on entities
 */
export class APIClient<T> {
  private endpoint: string;

  constructor(endpoint: string) {
    this.endpoint = endpoint;
  }

  /**
   * Get all entities with optional query parameters
   */
  getAll = async (
    params?: Record<string, any>
  ): Promise<{ data: T[]; meta?: any }> => {
    const queryString = params
      ? `?${new URLSearchParams(this.formatParams(params)).toString()}`
      : "";
    return fetchData<{ data: T[]; meta?: any }>(
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
   * Perform a custom query on the entity endpoint
   */
  query = async <R = T>(
    queryString: string,
    config?: AxiosRequestConfig
  ): Promise<R> => {
    return fetchData<R>(`${this.endpoint}/${queryString}`, config);
  };

  /**
   * Helper to format parameters for URL query strings
   * Handles nested objects and arrays
   */
  private formatParams(params: Record<string, any>): Record<string, string> {
    const result: Record<string, string> = {};

    Object.keys(params).forEach((key) => {
      const value = params[key];
      if (value !== undefined && value !== null) {
        result[key] =
          typeof value === "object" ? JSON.stringify(value) : String(value);
      }
    });

    return result;
  }
}
