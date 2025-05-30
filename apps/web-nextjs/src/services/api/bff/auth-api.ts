import { bffPostData, bffFetchData, bffPutData } from "./bff-client";
import { AuthRequest, AuthResponse } from "./types";
import { createLogger } from "@/utils/logging";

const logger = createLogger("BFFAuthAPI");

/**
 * BFF Authentication API - handles all auth operations through BFF
 * Using RESTful resource-oriented endpoints
 */
export const BFFAuthAPI = {
  /**
   * Login with email and password
   */
  login: async (credentials: AuthRequest): Promise<AuthResponse> => {
    logger.debug("Attempting login", { email: credentials.email });

    // Use new resource-oriented endpoint
    const response = await bffPostData<AuthResponse>(
      "/bff/v1/tokens",
      credentials
    );

    // Store token in localStorage
    if (typeof window !== "undefined" && response.access_token) {
      localStorage.setItem("auth_token", response.access_token);
      logger.debug("Auth token stored successfully");
    }

    return response;
  },

  /**
   * Register new user
   */
  register: async (
    userData: AuthRequest & { name?: string }
  ): Promise<AuthResponse> => {
    logger.debug("Attempting registration", { email: userData.email });

    // Use new resource-oriented endpoint
    const response = await bffPostData<AuthResponse>("/bff/v1/users", userData);

    // Store token in localStorage
    if (typeof window !== "undefined" && response.access_token) {
      localStorage.setItem("auth_token", response.access_token);
      logger.debug("Auth token stored after registration");
    }

    return response;
  },

  /**
   * Refresh access token
   */
  refreshToken: async (): Promise<AuthResponse> => {
    logger.debug("Refreshing access token");

    // Use new resource-oriented endpoint with PUT
    const response = await bffPutData<AuthResponse>("/bff/v1/tokens", {});

    // Update token in localStorage
    if (typeof window !== "undefined" && response.access_token) {
      localStorage.setItem("auth_token", response.access_token);
      logger.debug("Auth token refreshed successfully");
    }

    return response;
  },

  /**
   * Verify current token
   */
  verifyToken: async (): Promise<{
    valid: boolean;
    user?: { id: number; email: string; name?: string };
  }> => {
    logger.debug("Verifying current token");

    // Use new resource-oriented endpoint
    return bffPostData<{
      valid: boolean;
      user?: { id: number; email: string; name?: string };
    }>("/bff/v1/tokens/verify", {});
  },

  /**
   * Get current user info
   */
  getCurrentUser: async (): Promise<{
    id: number;
    email: string;
    name?: string;
  }> => {
    logger.debug("Fetching current user info");

    // Use new resource-oriented endpoint
    return bffFetchData<{ id: number; email: string; name?: string }>(
      "/bff/v1/users/me"
    );
  },

  /**
   * Logout user
   */
  logout: async (): Promise<void> => {
    logger.debug("Logging out user");

    // Clear token from localStorage
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
      logger.debug("Auth token cleared from localStorage");
    }

    // Note: BFF API doesn't have a logout endpoint, so we just clear local storage
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: (): boolean => {
    if (typeof window === "undefined") return false;

    const token = localStorage.getItem("auth_token");
    return !!token;
  },

  /**
   * Get stored auth token
   */
  getToken: (): string | null => {
    if (typeof window === "undefined") return null;

    return localStorage.getItem("auth_token");
  },
};
