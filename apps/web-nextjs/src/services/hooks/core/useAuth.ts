import { useAuthStore } from "@/store/auth";
import { useCallback, useMemo } from "react";
import { useAnalytics } from "./useAnalytics";

// Define specific permission and role types for better type checking
export type Permission =
  | "movies:read"
  | "movies:write"
  | "movies:delete"
  | "users:read"
  | "users:write"
  | "admin:access";

export type UserRole = "user" | "editor" | "admin";

// Role to permission mapping
const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  user: ["movies:read"],
  editor: ["movies:read", "movies:write"],
  admin: [
    "movies:read",
    "movies:write",
    "movies:delete",
    "users:read",
    "users:write",
    "admin:access",
  ],
};

/**
 * Enhanced auth hook with analytics integration and additional utility functions
 *
 * @returns Auth state and utility functions with automatic analytics tracking
 */
export function useAuth() {
  // Get base auth state from store
  const authState = useAuthStore();

  // Get analytics tracking
  const analytics = useAnalytics();

  // Extract commonly used values
  const { user, isAuthenticated } = authState;
  const {
    login: baseLogin,
    register: baseRegister,
    logout: baseLogout,
    clearError,
    isLoading,
    error,
  } = authState;

  /**
   * Enhanced login with analytics tracking
   */
  const login = useCallback(
    async (email: string, password: string) => {
      try {
        const result = await baseLogin(email, password);

        // Track successful login
        analytics.trackAuth("login", "email");

        return result;
      } catch (error) {
        // Track failed login attempt
        analytics.trackError(
          "auth_login_failed",
          error instanceof Error ? error.message : "Login failed",
          "useAuth.login"
        );
        throw error;
      }
    },
    [baseLogin, analytics]
  );

  /**
   * Enhanced register with analytics tracking
   */
  const register = useCallback(
    async (userData: {
      email: string;
      password: string;
      username: string;
      password_confirm: string;
    }) => {
      try {
        const result = await baseRegister(userData);

        // Track successful signup
        analytics.trackAuth("signup", "email");

        return result;
      } catch (error) {
        // Track failed signup attempt
        analytics.trackError(
          "auth_signup_failed",
          error instanceof Error ? error.message : "Signup failed",
          "useAuth.register"
        );
        throw error;
      }
    },
    [baseRegister, analytics]
  );

  /**
   * Enhanced logout with analytics tracking
   */
  const logout = useCallback(() => {
    try {
      // Track logout before actually logging out
      analytics.trackAuth("logout");

      const result = baseLogout();
      return result;
    } catch (error) {
      // Track logout error
      analytics.trackError(
        "auth_logout_failed",
        error instanceof Error ? error.message : "Logout failed",
        "useAuth.logout"
      );
      throw error;
    }
  }, [baseLogout, analytics]);

  /**
   * Check if the current user has a specific permission
   */
  const hasPermission = useCallback(
    (permission: Permission): boolean => {
      if (!isAuthenticated || !user) return false;

      // For simplicity, we'll check based on a hard-coded role
      // In a real app, you'd get this from the user object or JWT claims
      const userRole = user.id === 1 ? "admin" : "user";

      // Check if the user's role has the requested permission
      return ROLE_PERMISSIONS[userRole]?.includes(permission) || false;
    },
    [isAuthenticated, user]
  );

  /**
   * Check if the user has a specific role
   */
  const hasRole = useCallback(
    (role: UserRole): boolean => {
      if (!isAuthenticated || !user) return false;

      // For simplicity, hardcoded check
      // In a real app, this would come from the user object
      return user.id === 1 ? role === "admin" : role === "user";
    },
    [isAuthenticated, user]
  );

  /**
   * Get current user info with proper typing
   */
  const currentUser = useMemo(() => {
    if (!user) return null;

    return {
      ...user,
      // Add computed properties
      displayName: user.username || user.email.split("@")[0],
      // Mock role for demo
      role: user.id === 1 ? "admin" : ("user" as UserRole),
    };
  }, [user]);

  return {
    // Original auth state
    ...authState,

    // Original functionality for backward compatibility
    login,
    register,
    logout,
    clearError,
    isLoading,
    error,

    // Enhanced user object
    currentUser,

    // Permission utilities
    hasPermission,
    hasRole,

    // Convenience getters
    isAdmin: useMemo(() => hasRole("admin"), [hasRole]),
    isEditor: useMemo(() => hasRole("editor"), [hasRole]),
    isUser: useMemo(() => hasRole("user"), [hasRole]),
  };
}

/**
 * Hook to access the current user with proper typing
 *
 * @returns The current authenticated user or null
 */
export function useCurrentUser() {
  const { currentUser } = useAuth();
  return currentUser;
}

/**
 * Hook to easily check permissions
 *
 * @param requiredPermission The permission to check for
 * @returns Object with loading state and authorization status
 */
export function usePermission(requiredPermission: Permission) {
  const { isLoading, hasPermission } = useAuth();

  const isAuthorized = useMemo(
    () => hasPermission(requiredPermission),
    [hasPermission, requiredPermission]
  );

  return {
    isLoading,
    isAuthorized,
  };
}

export default useAuth;
