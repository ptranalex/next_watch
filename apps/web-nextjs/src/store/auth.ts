import { create } from "zustand";
import { persist } from "zustand/middleware";
import AuthTokenManager from "@/utils/authTokenManager";
import authService, { UserData, RegisterData } from "@/services/authService";
import { useEffect } from "react";

export interface AuthUser {
  id: number;
  email: string;
  username?: string;
}

export type AuthError = string | null;

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
        set({ isLoading: true, error: null, lastAuthAction: "login" });
        try {
          // Call authentication service
          await authService.login({ email, password });

          // Load user data
          return get().loadUser();
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : "Login failed",
            isLoading: false,
            isAuthenticated: false,
          });
          return false;
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true, error: null, lastAuthAction: "register" });
        try {
          // Register user
          await authService.register(data);

          // Automatically log in after registration
          return get().login(data.email, data.password);
        } catch (error) {
          set({
            error:
              error instanceof Error ? error.message : "Registration failed",
            isLoading: false,
          });
          return false;
        }
      },

      logout: () => {
        authService.logout();
        set({
          user: null,
          isAuthenticated: false,
          lastAuthAction: "logout",
          error: null,
        });
      },

      loadUser: async () => {
        // If token is not valid, don't even try
        if (!AuthTokenManager.isAccessTokenValid()) {
          // Check if we can refresh
          if (AuthTokenManager.isRefreshTokenValid()) {
            const refreshed = await authService.refreshToken();
            if (!refreshed) {
              set({ isAuthenticated: false, user: null });
              return false;
            }
          } else {
            set({ isAuthenticated: false, user: null });
            return false;
          }
        }

        set({ isLoading: true, lastAuthAction: "loadUser" });
        try {
          const userData = await authService.getCurrentUser();
          set({
            user: userData,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          return true;
        } catch (error) {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error:
              error instanceof Error
                ? error.message
                : "Failed to load user data",
          });
          return false;
        }
      },

      clearError: () => set({ error: null }),

      // Enhanced Actions
      checkAuthStatus: async () => {
        // Skip check if we're already loading or if we're authenticated and have user data
        if (get().isLoading || (get().isAuthenticated && get().user)) {
          return get().isAuthenticated;
        }

        // Check if we have a valid token
        if (AuthTokenManager.isAccessTokenValid()) {
          return get().loadUser();
        }

        // Try to refresh if possible
        if (AuthTokenManager.isRefreshTokenValid()) {
          const refreshed = await authService.refreshToken();
          if (refreshed) {
            return get().loadUser();
          }
        }

        // No valid token and couldn't refresh
        set({ isAuthenticated: false, user: null });
        return false;
      },

      hasPermission: (permission: string) => {
        // This is a placeholder - implement based on your user roles/permissions system
        const { user } = get();
        if (!user) return false;

        // Example: if user had a roles or permissions array
        // return user.permissions?.includes(permission) || false;

        return true; // Default to true for now
      },

      updateProfile: async (userData: Partial<AuthUser>) => {
        set({ isLoading: true, error: null, lastAuthAction: "updateProfile" });

        try {
          // You would need to implement this in your auth service
          // Example: const updatedUser = await authService.updateProfile(userData);

          // For now, just update the local state
          set({
            user: { ...get().user!, ...userData },
            isLoading: false,
          });

          return true;
        } catch (error) {
          set({
            isLoading: false,
            error:
              error instanceof Error
                ? error.message
                : "Failed to update profile",
          });

          return false;
        }
      },

      loginWithToken: async (token: string) => {
        set({ isLoading: true, error: null, lastAuthAction: "loginWithToken" });

        try {
          // Store token
          AuthTokenManager.setAccessToken(token);

          // Load user with the token
          return get().loadUser();
        } catch (error) {
          set({
            isLoading: false,
            error:
              error instanceof Error ? error.message : "Token login failed",
          });

          return false;
        }
      },

      // Handle token expiration
      handleTokenExpired: () => {
        console.warn("Token expired, logging out user");
        set({
          user: null,
          isAuthenticated: false,
          lastAuthAction: "token_expired",
          error: "Your session has expired. Please log in again.",
        });
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
    useAuthStore.getState().handleTokenExpired();
  });
}
