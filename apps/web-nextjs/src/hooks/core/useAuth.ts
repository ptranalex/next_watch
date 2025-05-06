import { useAuthStore } from "@/store/auth";
import { useCallback, useMemo } from "react";

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
 * Enhanced auth hook with additional utility functions
 *
 * @returns Auth state and utility functions
 */
export function useAuth() {
  // Get base auth state from store
  const authState = useAuthStore();

  // Extract commonly used values
  const { user, isAuthenticated } = authState;
  const { login, register, logout, clearError, isLoading, error } = authState;

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
