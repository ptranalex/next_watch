import config from "@/config";

/**
 * Token storage keys in localStorage
 */
const ACCESS_TOKEN_KEY = config.auth.tokenKey;
const REFRESH_TOKEN_KEY = `${ACCESS_TOKEN_KEY}_refresh`;

/**
 * Interface for the decoded JWT payload
 */
interface JwtPayload {
  sub: string; // User ID
  exp: number; // Expiration timestamp
  type: string; // Token type (access or refresh)
  email?: string;
  name?: string;
  role?: string;
  iat: number; // Issued at timestamp
}

// Track last token refresh to prevent too frequent refreshes
let lastRefreshAttempt = 0;
const REFRESH_COOLDOWN = 10000; // 10 seconds

// Predefined refresh thresholds (in milliseconds)
const REFRESH_THRESHOLDS = {
  PROACTIVE: 10 * 60 * 1000, // 10 minutes - early refresh
  NAVIGATION: 5 * 60 * 1000, // 5 minutes - during navigation
  WARNING: 2 * 60 * 1000, // 2 minutes - show warning
  CRITICAL: 30 * 1000, // 30 seconds - emergency refresh
};

/**
 * Auth token manager for handling JWT tokens
 */
const AuthTokenManager = {
  /**
   * Store both access and refresh tokens in localStorage
   */
  setTokens: (accessToken: string, refreshToken: string): void => {
    if (typeof window !== "undefined") {
      localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    }
  },

  /**
   * Set just the access token
   */
  setAccessToken: (token: string): void => {
    if (typeof window !== "undefined") {
      localStorage.setItem(ACCESS_TOKEN_KEY, token);
    }
  },

  /**
   * Set just the refresh token
   */
  setRefreshToken: (token: string): void => {
    if (typeof window !== "undefined") {
      localStorage.setItem(REFRESH_TOKEN_KEY, token);
    }
  },

  /**
   * Get the access token from localStorage
   */
  getAccessToken: (): string | null => {
    if (typeof window !== "undefined") {
      return localStorage.getItem(ACCESS_TOKEN_KEY);
    }
    return null;
  },

  /**
   * Get the refresh token from localStorage
   */
  getRefreshToken: (): string | null => {
    if (typeof window !== "undefined") {
      return localStorage.getItem(REFRESH_TOKEN_KEY);
    }
    return null;
  },

  /**
   * Remove both tokens from localStorage
   */
  removeTokens: (): void => {
    if (typeof window !== "undefined") {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
    }
  },

  /**
   * Check if an access token is present
   */
  hasAccessToken: (): boolean => {
    return !!AuthTokenManager.getAccessToken();
  },

  /**
   * Check if a refresh token is present
   */
  hasRefreshToken: (): boolean => {
    return !!AuthTokenManager.getRefreshToken();
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
   * Check if the current access token is valid (exists and not expired)
   */
  isAccessTokenValid: (): boolean => {
    const token = AuthTokenManager.getAccessToken();

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
      return payload.exp > currentTime && payload.type === "access";
    } catch (error) {
      console.error("Error validating token:", error);
      return false;
    }
  },

  /**
   * Check if the refresh token is valid
   */
  isRefreshTokenValid: (): boolean => {
    const token = AuthTokenManager.getRefreshToken();

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
      return payload.exp > currentTime && payload.type === "refresh";
    } catch (error) {
      console.error("Error validating refresh token:", error);
      return false;
    }
  },

  /**
   * Get user info from the access token
   */
  getUserInfo: (): {
    id: string;
    email?: string;
    name?: string;
    role?: string;
  } | null => {
    const token = AuthTokenManager.getAccessToken();

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

  /**
   * Get detailed token information including expiration time
   */
  getTokenInfo: (): {
    isValid: boolean;
    expiresAt: number;
    expiresIn: number;
    type: string;
  } | null => {
    const token = AuthTokenManager.getAccessToken();

    if (!token) {
      return null;
    }

    const payload = AuthTokenManager.decodeToken(token);

    if (!payload) {
      return null;
    }

    const expiresAt = payload.exp * 1000; // Convert to milliseconds
    const now = Date.now();

    return {
      isValid: expiresAt > now,
      expiresAt,
      expiresIn: Math.max(0, expiresAt - now),
      type: payload.type,
    };
  },

  /**
   * Get time until token expiration in milliseconds
   * Returns -1 if token is invalid or already expired
   */
  getTimeUntilExpiration: (): number => {
    const tokenInfo = AuthTokenManager.getTokenInfo();
    if (!tokenInfo || !tokenInfo.isValid) return -1;
    return tokenInfo.expiresIn;
  },

  /**
   * Check if token needs refresh based on the specified threshold
   * @param threshold Threshold in milliseconds or a predefined threshold name
   */
  shouldRefreshToken: (
    threshold: number | keyof typeof REFRESH_THRESHOLDS = "PROACTIVE"
  ): boolean => {
    const timeUntilExpiration = AuthTokenManager.getTimeUntilExpiration();
    if (timeUntilExpiration === -1) return false;

    // Determine actual threshold value
    const actualThreshold =
      typeof threshold === "number" ? threshold : REFRESH_THRESHOLDS[threshold];

    return timeUntilExpiration < actualThreshold;
  },

  /**
   * Check if token is critically close to expiration
   */
  isTokenCritical: (): boolean => {
    return AuthTokenManager.shouldRefreshToken("CRITICAL");
  },

  /**
   * Check if token is close enough to expiration to show a warning
   */
  shouldShowWarning: (): boolean => {
    return AuthTokenManager.shouldRefreshToken("WARNING");
  },

  /**
   * Check if token needs refresh during navigation
   */
  shouldRefreshForNavigation: (): boolean => {
    return AuthTokenManager.shouldRefreshToken("NAVIGATION");
  },

  /**
   * Check if refresh is allowed (not in cooldown period)
   */
  canAttemptRefresh: (): boolean => {
    const now = Date.now();
    return now - lastRefreshAttempt > REFRESH_COOLDOWN;
  },

  /**
   * Mark that a refresh attempt was made
   */
  markRefreshAttempt: (): void => {
    lastRefreshAttempt = Date.now();
  },

  /**
   * Get refresh threshold values for external use
   */
  getRefreshThresholds: () => REFRESH_THRESHOLDS,
};

export default AuthTokenManager;
