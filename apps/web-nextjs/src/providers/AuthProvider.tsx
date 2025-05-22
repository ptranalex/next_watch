"use client";

import React, { useEffect, useRef, useCallback } from "react";
import { useAuthStore } from "@/store/auth";
import SessionExpiredModal from "@/components/ui/molecules/SessionExpiredModal";
import AuthTokenManager from "@/utils/auth/authTokenManager";

/**
 * Auth provider component that handles auth initialization and recovery
 *
 * This component is responsible for:
 * 1. Checking auth status on mount
 * 2. Setting up background token refresh
 * 3. Handling token recovery attempts before showing session expired modals
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const {
    checkAuthStatus,
    setupTokenRefresh,
    isAuthenticated,
    error,
    handleTokenExpired,
    attemptTokenRefresh,
  } = useAuthStore();
  const recoveryAttemptCount = useRef(0);
  const MAX_RECOVERY_ATTEMPTS = 2;

  // Attempt to recover from token errors
  const attemptRecovery = useCallback(async () => {
    // Only try recovery if authenticated and have error
    if (!isAuthenticated || !error) return false;

    // If we've already tried too many times, don't attempt again
    if (recoveryAttemptCount.current >= MAX_RECOVERY_ATTEMPTS) {
      console.warn(
        `Auth: Max recovery attempts (${MAX_RECOVERY_ATTEMPTS}) reached, giving up`
      );
      return false;
    }

    // Check if it's a token-related error
    const tokenErrors = [
      "token",
      "session",
      "expired",
      "unauthorized",
      "authentication",
      "auth",
    ];

    const isTokenError = tokenErrors.some((term) =>
      error.toLowerCase().includes(term)
    );

    if (!isTokenError) return false;

    console.log(
      `Auth: Attempting recovery ***REMOVED***${
        recoveryAttemptCount.current + 1
      } for error: ${error}`
    );
    recoveryAttemptCount.current += 1;

    try {
      // Try refresh token using the centralized method
      if (AuthTokenManager.hasRefreshToken()) {
        console.log("Auth: Attempting token refresh as recovery");
        const success = await attemptTokenRefresh();

        if (success) {
          console.log("Auth: Recovery successful - token refreshed");
          await checkAuthStatus();
          return true;
        }
      }

      console.log("Auth: Recovery failed - could not refresh token");
      return false;
    } catch (e) {
      console.error("Auth: Error during recovery attempt", e);
      return false;
    }
  }, [isAuthenticated, error, checkAuthStatus, attemptTokenRefresh]);

  // Monitor for auth errors and attempt recovery
  useEffect(() => {
    if (error) {
      attemptRecovery().then((recovered) => {
        if (
          !recovered &&
          recoveryAttemptCount.current >= MAX_RECOVERY_ATTEMPTS
        ) {
          // All recovery attempts failed, trigger a definitive session expired
          console.log(
            "Auth: All recovery attempts failed, session truly expired"
          );
          handleTokenExpired();
        }
      });
    } else {
      // Reset recovery counter when there's no error
      recoveryAttemptCount.current = 0;
    }
  }, [error, attemptRecovery, handleTokenExpired]);

  // Setup token refresh on mount
  useEffect(() => {
    // Initial auth check
    checkAuthStatus();

    // Setup background token refresh
    const cleanupRefresh = setupTokenRefresh();

    // Setup debug logging for authentication state
    console.debug("Auth: Provider initialized, background refresh active");

    // Clean up on unmount
    return () => {
      cleanupRefresh();
      console.debug("Auth: Provider cleanup, background refresh stopped");
    };
  }, [checkAuthStatus, setupTokenRefresh]);

  return (
    <>
      {children}
      <SessionExpiredModal />
    </>
  );
};

export default AuthProvider;
