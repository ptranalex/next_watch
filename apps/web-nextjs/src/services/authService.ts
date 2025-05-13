import config from "@/config";
import AuthTokenManager from "@/utils/authTokenManager";

const API_URL = config.api.baseUrl;

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username?: string;
  password: string;
  password_confirm: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface UserData {
  id: number;
  email: string;
  username?: string;
}

/**
 * Service for handling authentication-related API calls
 */
const authService = {
  /**
   * Register a new user
   */
  register: async (data: RegisterData): Promise<UserData> => {
    const response = await fetch(`${API_URL}/api/v1/auth/signup/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: data.email,
        username: data.username,
        password: data.password,
        password_confirm: data.password_confirm,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Registration failed");
    }

    return response.json();
  },

  /**
   * Log in a user with email and password
   */
  login: async (credentials: LoginCredentials): Promise<AuthTokens> => {
    // Convert credentials to form data format
    const formData = new URLSearchParams();
    formData.append("username", credentials.email);
    formData.append("password", credentials.password);

    const response = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData.toString(),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Login failed");
    }

    const tokens = await response.json();

    // Store tokens
    AuthTokenManager.setTokens(tokens.access_token, tokens.refresh_token);

    return tokens;
  },

  /**
   * Get current user information
   */
  getCurrentUser: async (): Promise<UserData> => {
    const token = AuthTokenManager.getAccessToken();

    if (!token) {
      throw new Error("No authentication token found");
    }

    const response = await fetch(`${API_URL}/api/v1/auth/me/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Token might be expired, try to refresh
        const refreshed = await authService.refreshToken();
        if (refreshed) {
          // Retry with new token
          return authService.getCurrentUser();
        }
        throw new Error("Session expired");
      }
      throw new Error("Failed to get user data");
    }

    return response.json();
  },

  /**
   * Refresh the access token using refresh token
   */
  refreshToken: async (): Promise<boolean> => {
    const refreshToken = AuthTokenManager.getRefreshToken();

    if (!refreshToken) {
      return false;
    }

    // Prevent too frequent refresh attempts
    if (!AuthTokenManager.canAttemptRefresh()) {
      return true; // Return true to prevent error states during cooldown
    }

    AuthTokenManager.markRefreshAttempt();

    try {
      // Use the correct endpoint without trailing slash
      // Send JSON payload instead of form data as the API expects a JSON object with refresh_token field
      const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        const status = response.status;

        // Handle specific error cases
        if (status === 401 || status === 403) {
          // The refresh token itself is invalid or expired
          authService.logout();
          return false;
        }

        if (status >= 500) {
          // Server error - might be temporary, don't invalidate session yet
          return false;
        }

        return false;
      }

      const tokens = await response.json();
      AuthTokenManager.setTokens(tokens.access_token, tokens.refresh_token);
      return true;
    } catch {
      return false;
    }
  },

  /**
   * Log out the current user
   */
  logout: (): void => {
    AuthTokenManager.removeTokens();
  },
};

export default authService;
