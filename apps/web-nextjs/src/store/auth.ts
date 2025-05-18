import { create } from "zustand";
import { persist } from "zustand/middleware";
import AuthTokenManager from "@/utils/auth/authTokenManager";
import { AuthAPI } from "@/services/api/auth/auth-api";
import type { RegisterData } from "@/services/api/auth/types";
import { createLogger } from "@/utils/logging";

// Create logger for this store
const logger = createLogger("authStore");

// Add a type declaration for the global window object
declare global {
  interface Window {
    __tokenRefreshInterval?: NodeJS.Timeout;
    __navigationObserver?: MutationObserver;
  }
}

export interface AuthUser {
  id: number;
  email: string;
  username?: string;
  // Add permissions field for future implementation
  permissions?: string[];
  role?: string;
}

export type AuthError = string | null;

/**
 * Formats an error into a standardized error message
 */
const formatError = (error: unknown, fallback: string): string => {
  if (error instanceof Error) return `${fallback}: ${error.message}`;
  if (typeof error === "string") return error;
  return fallback;
};

/**
 * Refresh strategy states
 */
type RefreshStrategy = {
  scheduled: boolean;
  navigation: boolean;
};

interface AuthState {
  // State
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: AuthError;
  lastAuthAction: string | null;

  // Basic Actions
  login: (email: string, password: string) => Promise<boolean>;
  register: (data: RegisterData) => Promise<boolean>;
  logout: () => void;
  loadUser: () => Promise<boolean>;
  clearError: () => void;

  // Enhanced Actions
  checkAuthStatus: () => Promise<boolean>;
  hasPermission: (permission: string) => boolean;
  updateProfile: (userData: Partial<AuthUser>) => Promise<boolean>;
  loginWithToken: (token: string) => Promise<boolean>;

  // Session management
  handleTokenExpired: () => void;
  attemptTokenRefresh: () => Promise<boolean>;

  // Refresh management
  setupTokenRefresh: () => () => void;
  enableRefreshStrategy: (
    strategy: keyof RefreshStrategy,
    enable: boolean
  ) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      lastAuthAction: null,

      // Basic Actions
      login: async (email: string, password: string) => {
        logger.info(`Login attempt for: ${email}`);
        set({ isLoading: true, error: null, lastAuthAction: "login" });
        try {
          // Call authentication service
          await AuthAPI.login({ email, password });
          logger.info("Login successful, loading user data");

          // Load user data
          return get().loadUser();
        } catch (error) {
          logger.error("Login failed:", error);
          set({
            error: formatError(error, "Login failed"),
            isLoading: false,
            isAuthenticated: false,
          });
          return false;
        }
      },

      register: async (data: RegisterData) => {
        logger.info(`Registration attempt for: ${data.email}`);
        set({ isLoading: true, error: null, lastAuthAction: "register" });
        try {
          // Register user
          await AuthAPI.register(data);
          logger.info("Registration successful, attempting login");

          // Automatically log in after registration
          return get().login(data.email, data.password);
        } catch (error) {
          logger.error("Registration failed:", error);
          set({
            error: formatError(error, "Registration failed"),
            isLoading: false,
          });
          return false;
        }
      },

      logout: () => {
        logger.info("Logging out user");
        AuthAPI.logout();
        set({
          user: null,
          isAuthenticated: false,
          lastAuthAction: "logout",
          error: null,
        });
      },

      loadUser: async () => {
        // If token is not valid, try to refresh first
        if (!AuthTokenManager.isAccessTokenValid()) {
          logger.debug("Access token invalid, attempting refresh");
          if (AuthTokenManager.isRefreshTokenValid()) {
            const refreshed = await AuthAPI.refreshToken();
            if (!refreshed) {
              logger.warn("Token refresh failed, user not authenticated");
              set({ isAuthenticated: false, user: null });
              return false;
            }
            logger.debug("Token refreshed successfully");
          } else {
            logger.debug("Refresh token also invalid, user not authenticated");
            set({ isAuthenticated: false, user: null });
            return false;
          }
        }

        logger.debug("Loading user data");
        set({ isLoading: true, lastAuthAction: "loadUser" });
        try {
          const userData = await AuthAPI.getCurrentUser();
          logger.info(`User loaded: ${userData.email} (ID: ${userData.id})`);
          set({
            user: userData,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          return true;
        } catch (error) {
          logger.error("Failed to load user data:", error);
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: formatError(error, "Failed to load user data"),
          });
          return false;
        }
      },

      clearError: () => {
        logger.debug("Clearing auth errors");
        set({ error: null });
      },

      // Enhanced Actions
      checkAuthStatus: async () => {
        // Skip check if we're already loading or if we're authenticated and have user data
        if (get().isLoading || (get().isAuthenticated && get().user)) {
          logger.debug(
            "Skipping auth check - already authenticated or loading"
          );
          return get().isAuthenticated;
        }

        // Check if we have a valid token
        if (AuthTokenManager.isAccessTokenValid()) {
          logger.debug("Access token valid, loading user data");
          return get().loadUser();
        }

        // Try to refresh if possible
        if (AuthTokenManager.isRefreshTokenValid()) {
          logger.debug(
            "Access token invalid but refresh token valid, attempting refresh"
          );
          const refreshed = await AuthAPI.refreshToken();
          if (refreshed) {
            logger.debug("Token refreshed successfully, loading user data");
            return get().loadUser();
          }
          logger.debug("Token refresh failed");
        }

        // No valid token and couldn't refresh
        logger.debug("No valid tokens, user not authenticated");
        set({ isAuthenticated: false, user: null });
        return false;
      },

      hasPermission: (permission: string) => {
        // Get the current user
        const { user } = get();
        if (!user) {
          logger.debug(
            `Permission check failed (${permission}): No user logged in`
          );
          return false;
        }

        // If user has explicit permissions array, use it
        if (user.permissions?.length) {
          const hasPermission = user.permissions.includes(permission);
          logger.debug(
            `Permission check (${permission}): ${
              hasPermission ? "Granted" : "Denied"
            }`
          );
          return hasPermission;
        }

        // Fallback to role-based permission check
        if (user.role === "admin") {
          logger.debug(
            `Permission check (${permission}): Granted due to admin role`
          );
          return true;
        }

        // For demo, grant basic permissions to all authenticated users
        const basicPermissions = ["movies:read"];
        const hasBasicPermission = basicPermissions.includes(permission);
        logger.debug(
          `Basic permission check (${permission}): ${
            hasBasicPermission ? "Granted" : "Denied"
          }`
        );
        return hasBasicPermission;
      },

      updateProfile: async (userData: Partial<AuthUser>) => {
        logger.info("Updating user profile");
        set({ isLoading: true, error: null, lastAuthAction: "updateProfile" });

        try {
          // You would need to implement this in your auth service
          // Example: const updatedUser = await authService.updateProfile(userData);

          // For now, just update the local state
          logger.info("Profile updated successfully");
          set({
            user: { ...get().user!, ...userData },
            isLoading: false,
          });

          return true;
        } catch (error) {
          logger.error("Failed to update profile:", error);
          set({
            isLoading: false,
            error: formatError(error, "Failed to update profile"),
          });

          return false;
        }
      },

      loginWithToken: async (token: string) => {
        logger.info("Attempting login with token");
        set({ isLoading: true, error: null, lastAuthAction: "loginWithToken" });

        try {
          // Store token
          AuthTokenManager.setAccessToken(token);
          logger.debug("Token stored, loading user data");

          // Load user with the token
          return get().loadUser();
        } catch (error) {
          logger.error("Token login failed:", error);
          set({
            isLoading: false,
            error: formatError(error, "Token login failed"),
          });

          return false;
        }
      },

      // Handle token expiration
      handleTokenExpired: () => {
        logger.warn("Token expired, logging user out");
        set({
          user: null,
          isAuthenticated: false,
          lastAuthAction: "token_expired",
          error: "Your session has expired. Please log in again.",
        });
      },

      // Attempt token refresh
      attemptTokenRefresh: async (): Promise<boolean> => {
        const { isAuthenticated } = get();

        // Don't attempt refresh if not authenticated
        if (!isAuthenticated) {
          logger.debug("Not attempting refresh - user not authenticated");
          return false;
        }

        try {
          logger.debug("Attempting token refresh");
          const refreshed = await AuthAPI.refreshToken();

          if (refreshed) {
            logger.info("Token refreshed successfully");
            return true;
          }

          // Check if the refresh token is valid to determine if we should logout
          if (!AuthTokenManager.isRefreshTokenValid()) {
            logger.warn("Refresh token invalid, authentication will be lost");
            return false;
          }

          // Token refresh failed but refresh token still valid (possibly temporary server issue)
          logger.warn(
            "Token refresh failed but refresh token still valid (temporary issue?)"
          );
          return false;
        } catch (error) {
          logger.error("Token refresh attempt failed:", error);
          return false;
        }
      },

      // Enable or disable specific refresh strategies
      enableRefreshStrategy: (
        strategy: keyof RefreshStrategy,
        enable: boolean
      ) => {
        // This is used to control which refresh strategies are active
        logger.debug(
          `${enable ? "Enabling" : "Disabling"} refresh strategy: ${strategy}`
        );

        // Implementation depends on the strategy
        if (strategy === "navigation" && typeof window !== "undefined") {
          // Clean up existing observer if disabling
          if (!enable && window.__navigationObserver) {
            logger.debug("Cleaning up navigation observer");
            window.__navigationObserver.disconnect();
            window.__navigationObserver = undefined;
          }
        }
      },

      // Setup background token refresh
      setupTokenRefresh: () => {
        logger.info("Setting up token refresh mechanisms");

        // Track last handled navigation to prevent duplicate refreshes
        let lastNavigationTime = 0;
        const NAVIGATION_COOLDOWN = 1000; // 1 second cooldown

        // Set up scheduled background refresh
        const intervalId = setInterval(async () => {
          const { isAuthenticated } = get();
          if (!isAuthenticated) return;

          // Check if token needs refresh based on predefined thresholds
          if (AuthTokenManager.shouldRefreshToken()) {
            logger.debug("Token refresh needed based on scheduled check");
            await get().attemptTokenRefresh();
          }
          // If token is critical but refresh failed, we might want to warn the user
          else if (AuthTokenManager.isTokenCritical()) {
            logger.warn("Token critically close to expiration");
            // This could trigger a warning UI
          }
        }, 60000); // Check every minute

        // Setup navigation event handling with MutationObserver
        if (typeof window !== "undefined") {
          // Handle route change for any navigation
          const handleRouteChange = async () => {
            const now = Date.now();
            // Skip if we recently handled a navigation
            if (now - lastNavigationTime < NAVIGATION_COOLDOWN) return;
            lastNavigationTime = now;

            const { isAuthenticated } = get();
            if (!isAuthenticated) return;

            // Check if we should refresh for navigation (using dedicated threshold)
            if (AuthTokenManager.shouldRefreshForNavigation()) {
              logger.debug("Token refresh needed for navigation");
              await get().attemptTokenRefresh();
            }
          };

          // Create the mutation observer to detect navigation
          const observer = new MutationObserver((mutations) => {
            // Only check when body content changes (good proxy for navigation)
            if (mutations.some((m) => m.target === document.body)) {
              handleRouteChange();
            }
          });

          // Start observing
          observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: false,
            characterData: false,
          });

          logger.debug("Navigation observer set up for token refresh");

          // Store for cleanup
          window.__navigationObserver = observer;
        }

        // Store interval ID for cleanup
        if (typeof window !== "undefined") {
          window.__tokenRefreshInterval = intervalId;
        }

        // Return cleanup function
        return () => {
          logger.debug("Cleaning up token refresh mechanisms");

          if (typeof window !== "undefined") {
            // Clean up interval
            if (window.__tokenRefreshInterval) {
              clearInterval(window.__tokenRefreshInterval);
              window.__tokenRefreshInterval = undefined;
            }

            // Clean up mutation observer
            if (window.__navigationObserver) {
              window.__navigationObserver.disconnect();
              window.__navigationObserver = undefined;
            }
          }
        };
      },
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// Setup token expiration listener
if (typeof window !== "undefined") {
  window.addEventListener("auth:token-expired", () => {
    logger.warn("auth:token-expired event received");
    useAuthStore.getState().handleTokenExpired();
  });
}
