import axios, { AxiosRequestConfig } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create API client instance
export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add a request interceptor to handle authentication
apiClient.interceptors.request.use(
  (config) => {
    // Get the token from localStorage if we're in the browser
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("auth_token");
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
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
          localStorage.removeItem("auth_token");
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
