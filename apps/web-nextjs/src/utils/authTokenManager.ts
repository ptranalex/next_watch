import config from "@/src/config";

/**
 * Token storage key in localStorage
 */
const TOKEN_KEY = config.auth.tokenKey;

/**
 * Interface for the decoded JWT payload
 */
interface JwtPayload {
  sub: string; // User ID
  exp: number; // Expiration timestamp
  email?: string;
  name?: string;
  role?: string;
}

/**
 * Auth token manager for handling JWT tokens
 */
const AuthTokenManager = {
  /**
   * Store the JWT token in localStorage
   */
  setToken: (token: string): void => {
    if (typeof window !== "undefined") {
      localStorage.setItem(TOKEN_KEY, token);
    }
  },

  /**
   * Get the JWT token from localStorage
   */
  getToken: (): string | null => {
    if (typeof window !== "undefined") {
      return localStorage.getItem(TOKEN_KEY);
    }
    return null;
  },

  /**
   * Remove the JWT token from localStorage
   */
  removeToken: (): void => {
    if (typeof window !== "undefined") {
      localStorage.removeItem(TOKEN_KEY);
    }
  },

  /**
   * Check if a token is present
   */
  hasToken: (): boolean => {
    return !!AuthTokenManager.getToken();
  },

  /**
   * Decode the JWT token to get the payload
   */
  decodeToken: (token: string): JwtPayload | null => {
    try {
      const base64Url = token.split(".")[1];
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split("")
          .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
          .join("")
      );

      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error("Failed to decode token:", error);
      return null;
    }
  },

  /**
   * Check if the current token is valid (exists and not expired)
   */
  isTokenValid: (): boolean => {
    const token = AuthTokenManager.getToken();

    if (!token) {
      return false;
    }

    try {
      const payload = AuthTokenManager.decodeToken(token);

      if (!payload) {
        return false;
      }

      // Check if token has expired
      const currentTime = Math.floor(Date.now() / 1000);
      return payload.exp > currentTime;
    } catch (error) {
      console.error("Error validating token:", error);
      return false;
    }
  },

  /**
   * Get user info from the token
   */
  getUserInfo: (): {
    id: string;
    email?: string;
    name?: string;
    role?: string;
  } | null => {
    const token = AuthTokenManager.getToken();

    if (!token) {
      return null;
    }

    const payload = AuthTokenManager.decodeToken(token);

    if (!payload) {
      return null;
    }

    return {
      id: payload.sub,
      email: payload.email,
      name: payload.name,
      role: payload.role,
    };
  },
};

export default AuthTokenManager;
