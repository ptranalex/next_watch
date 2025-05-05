"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/store/auth";

/**
 * Component that initializes authentication on application startup
 * Place this in your root layout to ensure auth is checked on initial load
 */
const AuthInitializer = () => {
  const checkAuthStatus = useAuthStore((state) => state.checkAuthStatus);

  useEffect(() => {
    // Check authentication status on app initialization
    checkAuthStatus();

    // Set up an interval to periodically refresh tokens in the background
    const refreshInterval = setInterval(() => {
      const isAuthenticated = useAuthStore.getState().isAuthenticated;
      if (isAuthenticated) {
        checkAuthStatus();
      }
    }, 15 * 60 * 1000); // Check every 15 minutes

    return () => clearInterval(refreshInterval);
  }, [checkAuthStatus]);

  // This component doesn't render anything
  return null;
};

export default AuthInitializer;
