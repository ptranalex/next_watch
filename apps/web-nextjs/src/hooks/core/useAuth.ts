import { useAuthStore, AuthUser } from "@/store/auth";

/**
 * Hook for accessing user authentication data
 */
export const useAuth = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const error = useAuthStore((state) => state.error);
  const clearError = useAuthStore((state) => state.clearError);
  const isLoading = useAuthStore((state) => state.isLoading);

  return {
    isAuthenticated,
    user,
    logout,
    error,
    clearError,
    isLoading,
  };
};

/**
 * Hook for login functionality
 */
export const useLogin = () => {
  const login = useAuthStore((state) => state.login);
  const isLoading = useAuthStore((state) => state.isLoading);
  const error = useAuthStore((state) => state.error);
  const clearError = useAuthStore((state) => state.clearError);

  return { login, isLoading, error, clearError };
};

/**
 * Hook for registration functionality
 */
export const useRegister = () => {
  const register = useAuthStore((state) => state.register);
  const isLoading = useAuthStore((state) => state.isLoading);
  const error = useAuthStore((state) => state.error);
  const clearError = useAuthStore((state) => state.clearError);

  return { register, isLoading, error, clearError };
};

/**
 * Hook for checking if user is authenticated
 */
export const useAuthCheck = () => {
  return useAuthStore((state) => state.isAuthenticated);
};

/**
 * Hook for accessing current user data
 */
export const useUser = () => {
  return useAuthStore((state) => state.user);
};
