import { fetchData, postData } from "../core/api-client";
import { APIError, AuthError, NetworkError } from "../core/errors";
import { createLogger } from "@/utils/logging";
import AuthTokenManager from "@/utils/auth/authTokenManager";
import { LoginCredentials, RegisterData, AuthTokens, UserData } from "./types";

// Create dedicated logger for auth API
const logger = createLogger("AuthAPI");

/**
 * Authentication API Client
 *
 * Provides methods for user authentication, registration, and token management.
 */
export const AuthAPI = {
  /**
   * Register a new user
   */
  register: async (data: RegisterData): Promise<UserData> => {
    logger.info(`Registering new user with email: ${data.email}`);

    try {
      const userData = await postData<UserData>("/api/v1/auth/signup/", {
        email: data.email,
        username: data.username,
        password: data.password,
        password_confirm: data.password_confirm,
      });

      logger.info(`Successfully registered user: ${data.email}`);
      return userData;
    } catch (error) {
      logger.error(`Registration failed for email: ${data.email}`, error);

      if (error instanceof APIError) {
        throw new Error(error.message || "Registration failed");
      }

      throw new Error("Registration failed due to network or server error");
    }
  },

  /**
   * Log in a user with email and password
   */
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    logger.info(`Attempting login for user: ${credentials.email}`);

    try {
      // Convert credentials to form data format
      const formData = new URLSearchParams();
      formData.append("username", credentials.email);
      formData.append("password", credentials.password);

      // Using postData directly with special content type header
      const tokens = await postData<AuthTokens>(
        "/api/v1/auth/login",
        { username: credentials.email, password: credentials.password },
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          transformRequest: [
            (data) => {
              const formData = new URLSearchParams();
              for (const key in data) {
                formData.append(key, data[key]);
              }
              return formData.toString();
            },
          ],
        }
      );

      // Store tokens
      AuthTokenManager.setTokens(tokens.access_token, tokens.refresh_token);
      logger.info(`Login successful for user: ${credentials.email}`);
      logger.debug("Auth tokens received and stored");

      return tokens;
    } catch (error) {
      logger.error(`Login failed for email: ${credentials.email}`, error);

      if (error instanceof AuthError) {
        throw new Error(error.message || "Login failed: Invalid credentials");
      } else if (error instanceof APIError) {
        throw new Error(error.message || "Login failed");
      }

      throw new Error("Login failed due to network or server error");
    }
  },

  /**
   * Get current user information
   */
  getCurrentUser: async (): Promise<UserData> => {
    logger.debug("Getting current user information");
    const token = AuthTokenManager.getAccessToken();

    if (!token) {
      logger.warn("No authentication token found when getting current user");
      throw new Error("No authentication token found");
    }

    try {
      // Using the API client which already handles auth headers
      const userData = await fetchData<UserData>("/api/v1/auth/me/");
      logger.debug(`Current user data retrieved for ID: ${userData.id}`);
      return userData;
    } catch (error) {
      if (error instanceof AuthError) {
        logger.warn(
          "Authentication error when getting user data, attempting token refresh"
        );

        // Token might be expired, try to refresh
        const refreshed = await AuthAPI.refreshToken();
        if (refreshed) {
          logger.info("Token refreshed successfully, retrying user data fetch");
          // Retry with new token
          return AuthAPI.getCurrentUser();
        }

        logger.error("Session expired, couldn't refresh token");
        throw new Error("Session expired");
      }

      logger.error("Failed to get user data", error);
      throw new Error("Failed to get user data");
    }
  },

  /**
   * Refresh the access token using refresh token
   */
  refreshToken: async (): Promise<boolean> => {
    logger.debug("Attempting to refresh access token");
    const refreshToken = AuthTokenManager.getRefreshToken();

    if (!refreshToken) {
      logger.warn("No refresh token found");
      return false;
    }

    // Prevent too frequent refresh attempts
    if (!AuthTokenManager.canAttemptRefresh()) {
      logger.debug("Refresh attempt too soon after previous attempt, skipping");
      return true; // Return true to prevent error states during cooldown
    }

    AuthTokenManager.markRefreshAttempt();
    logger.debug("Refresh attempt marked");

    try {
      // Use the API client for the refresh token request
      const tokens = await postData<AuthTokens>("/api/v1/auth/refresh", {
        refresh_token: refreshToken,
      });

      AuthTokenManager.setTokens(tokens.access_token, tokens.refresh_token);
      logger.info("Token refreshed successfully");
      return true;
    } catch (error) {
      if (error instanceof AuthError) {
        logger.warn("Authentication error during token refresh, logging out");
        // The refresh token itself is invalid or expired
        AuthAPI.logout();
        return false;
      }

      if (error instanceof NetworkError) {
        logger.error("Network error during token refresh", error);
        return false;
      }

      if (error instanceof APIError) {
        const statusCode = (error as any)?.statusCode || 0;

        if (statusCode >= 500) {
          logger.error(
            `Server error (${statusCode}) during token refresh`,
            error
          );
          // Server error - might be temporary, don't invalidate session yet
          return false;
        }

        logger.error(`API error (${statusCode}) during token refresh`, error);
        return false;
      }

      logger.error("Unknown error during token refresh", error);
      return false;
    }
  },

  /**
   * Log out the current user
   */
  logout: (): void => {
    logger.info("User logged out");
    AuthTokenManager.removeTokens();
  },

  /**
   * Check if the current user is authenticated
   */
  isAuthenticated: (): boolean => {
    return AuthTokenManager.isAccessTokenValid();
  },

  /**
   * Get information about token validity and expiration
   */
  getTokenInfo: () => {
    return AuthTokenManager.getTokenInfo();
  },

  /**
   * Check if token needs refresh
   */
  shouldRefreshToken: (threshold?: number) => {
    return AuthTokenManager.shouldRefreshToken(threshold);
  },
};
