import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";

interface ProtectedRouteOptions {
  redirectUrl?: string;
  requiredPermission?: string;
}

/**
 * Hook for protecting routes that require authentication
 *
 * @param options Configuration options for the protected route
 * @returns Object containing loading state and whether the user is authorized
 */
export const useProtectedRoute = (options: ProtectedRouteOptions = {}) => {
  const { redirectUrl = "/", requiredPermission } = options;

  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isLoading = useAuthStore((state) => state.isLoading);
  const checkAuthStatus = useAuthStore((state) => state.checkAuthStatus);
  const hasPermission = useAuthStore((state) => state.hasPermission);

  useEffect(() => {
    const verifyAuth = async () => {
      setIsChecking(true);

      // First check the auth status (which may refresh tokens if needed)
      const isAuthed = await checkAuthStatus();

      if (!isAuthed) {
        // Not authenticated, redirect to home page so login modal can be shown
        router.push(redirectUrl);
        return;
      }

      if (requiredPermission && !hasPermission(requiredPermission)) {
        // Authenticated but lacks permission, redirect to unauthorized page
        router.push("/unauthorized");
        return;
      }

      setIsChecking(false);
    };

    verifyAuth();
  }, [checkAuthStatus, hasPermission, redirectUrl, requiredPermission, router]);

  // Return true if authorized (authenticated and has permission if specified)
  const isAuthorized =
    isAuthenticated &&
    (!requiredPermission || hasPermission(requiredPermission));

  return {
    isLoading: isLoading || isChecking,
    isAuthorized,
  };
};
