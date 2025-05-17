import config from "@/config";
import { createLogger } from "@/utils/logging";

// Create logger for this module
const logger = createLogger("AuthTokenManager");

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
      logger.debug("Access and refresh tokens stored");
    }
  },

  /**
   * Set just the access token
   */
  setAccessToken: (token: string): void => {
    if (typeof window !== "undefined") {
      localStorage.setItem(ACCESS_TOKEN_KEY, token);
      logger.debug("Access token stored");
    }
  },

  /**
   * Set just the refresh token
   */
  setRefreshToken: (token: string): void => {
    if (typeof window !== "undefined") {
      localStorage.setItem(REFRESH_TOKEN_KEY, token);
      logger.debug("Refresh token stored");
    }
  },

  /**
   * Get the access token from localStorage
   */
  getAccessToken: (): string | null => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem(ACCESS_TOKEN_KEY);
      logger.debug(`Access token ${token ? "retrieved" : "not found"}`);
      return token;
    }
    return null;
  },

  /**
   * Get the refresh token from localStorage
   */
  getRefreshToken: (): string | null => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem(REFRESH_TOKEN_KEY);
      logger.debug(`Refresh token ${token ? "retrieved" : "not found"}`);
      return token;
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
      logger.info("All tokens removed");
    }
  },

  /**
   * Check if an access token is present
   */
  hasAccessToken: (): boolean => {
    const hasToken = !!AuthTokenManager.getAccessToken();
    logger.debug(`Access token presence check: ${hasToken}`);
    return hasToken;
  },

  /**
   * Check if a refresh token is present
   */
  hasRefreshToken: (): boolean => {
    const hasToken = !!AuthTokenManager.getRefreshToken();
    logger.debug(`Refresh token presence check: ${hasToken}`);
    return hasToken;
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

      const payload = JSON.parse(jsonPayload);
      logger.debug(`Token decoded successfully, type: ${payload.type}`);
      return payload;
    } catch (error) {
      logger.error("Failed to decode token:", error);
      return null;
    }
  },

  /**
   * Check if the current access token is valid (exists and not expired)
   */
  isAccessTokenValid: (): boolean => {
    const token = AuthTokenManager.getAccessToken();

    if (!token) {
      logger.debug("Access token validation failed: No token");
      return false;
    }

    try {
      const payload = AuthTokenManager.decodeToken(token);

      if (!payload) {
        logger.debug("Access token validation failed: Invalid format");
        return false;
      }

      // Check if token has expired
      const currentTime = Math.floor(Date.now() / 1000);
      const isValid = payload.exp > currentTime && payload.type === "access";

      if (isValid) {
        const timeRemaining = payload.exp - currentTime;
        logger.debug(`Access token valid, expires in ${timeRemaining} seconds`);
      } else {
        if (payload.exp <= currentTime) {
          logger.debug("Access token validation failed: Token expired");
        }
        if (payload.type !== "access") {
          logger.debug(
            `Access token validation failed: Wrong token type (${payload.type})`
          );
        }
      }

      return isValid;
    } catch (error) {
      logger.error("Error validating access token:", error);
      return false;
    }
  },

  /**
   * Check if the refresh token is valid
   */
  isRefreshTokenValid: (): boolean => {
    const token = AuthTokenManager.getRefreshToken();

    if (!token) {
      logger.debug("Refresh token validation failed: No token");
      return false;
    }

    try {
      const payload = AuthTokenManager.decodeToken(token);

      if (!payload) {
        logger.debug("Refresh token validation failed: Invalid format");
        return false;
      }

      // Check if token has expired
      const currentTime = Math.floor(Date.now() / 1000);
      const isValid = payload.exp > currentTime && payload.type === "refresh";

      if (isValid) {
        const timeRemaining = payload.exp - currentTime;
        logger.debug(
          `Refresh token valid, expires in ${timeRemaining} seconds`
        );
      } else {
        if (payload.exp <= currentTime) {
          logger.debug("Refresh token validation failed: Token expired");
        }
        if (payload.type !== "refresh") {
          logger.debug(
            `Refresh token validation failed: Wrong token type (${payload.type})`
          );
        }
      }

      return isValid;
    } catch (error) {
      logger.error("Error validating refresh token:", error);
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
      logger.debug("Cannot get user info: No access token");
      return null;
    }

    const payload = AuthTokenManager.decodeToken(token);

    if (!payload) {
      logger.debug("Cannot get user info: Failed to decode token");
      return null;
    }

    logger.debug(`Retrieved user info from token for user ID: ${payload.sub}`);
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
      logger.debug("Cannot get token info: No access token");
      return null;
    }

    const payload = AuthTokenManager.decodeToken(token);

    if (!payload) {
      logger.debug("Cannot get token info: Failed to decode token");
      return null;
    }

    const expiresAt = payload.exp * 1000; // Convert to milliseconds
    const now = Date.now();
    const expiresIn = Math.max(0, expiresAt - now);

    logger.debug(
      `Token info retrieved: type=${payload.type}, expires in ${Math.floor(
        expiresIn / 1000
      )} seconds`
    );
    return {
      isValid: expiresAt > now,
      expiresAt,
      expiresIn,
      type: payload.type,
    };
  },

  /**
   * Get time until token expiration in milliseconds
   * Returns -1 if token is invalid or already expired
   */
  getTimeUntilExpiration: (): number => {
    const tokenInfo = AuthTokenManager.getTokenInfo();
    if (!tokenInfo || !tokenInfo.isValid) {
      logger.debug("Token expiration check: Token invalid or expired");
      return -1;
    }
    logger.debug(
      `Time until expiration: ${Math.floor(tokenInfo.expiresIn / 1000)} seconds`
    );
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

    const shouldRefresh = timeUntilExpiration < actualThreshold;
    if (shouldRefresh) {
      logger.debug(
        `Token refresh needed: ${Math.floor(
          timeUntilExpiration / 1000
        )}s remaining, threshold: ${Math.floor(actualThreshold / 1000)}s`
      );
    }

    return shouldRefresh;
  },

  /**
   * Check if token is critically close to expiration
   */
  isTokenCritical: (): boolean => {
    const isCritical = AuthTokenManager.shouldRefreshToken("CRITICAL");
    if (isCritical) {
      logger.warn("Token critically close to expiration");
    }
    return isCritical;
  },

  /**
   * Check if token is close enough to expiration to show a warning
   */
  shouldShowWarning: (): boolean => {
    const shouldWarn = AuthTokenManager.shouldRefreshToken("WARNING");
    if (shouldWarn) {
      logger.warn("Token close to expiration, warning threshold reached");
    }
    return shouldWarn;
  },

  /**
   * Check if token needs refresh during navigation
   */
  shouldRefreshForNavigation: (): boolean => {
    const shouldRefresh = AuthTokenManager.shouldRefreshToken("NAVIGATION");
    if (shouldRefresh) {
      logger.debug("Token needs refresh for navigation");
    }
    return shouldRefresh;
  },

  /**
   * Check if refresh is allowed (not in cooldown period)
   */
  canAttemptRefresh: (): boolean => {
    const now = Date.now();
    const canRefresh = now - lastRefreshAttempt > REFRESH_COOLDOWN;

    if (!canRefresh) {
      logger.debug(
        `Refresh attempt rejected: In cooldown period (${Math.floor(
          (REFRESH_COOLDOWN - (now - lastRefreshAttempt)) / 1000
        )}s remaining)`
      );
    }

    return canRefresh;
  },

  /**
   * Mark that a refresh attempt was made
   */
  markRefreshAttempt: (): void => {
    lastRefreshAttempt = Date.now();
    logger.debug("Refresh attempt marked at current time");
  },

  /**
   * Get refresh threshold values for external use
   */
  getRefreshThresholds: () => REFRESH_THRESHOLDS,
};

export default AuthTokenManager;
