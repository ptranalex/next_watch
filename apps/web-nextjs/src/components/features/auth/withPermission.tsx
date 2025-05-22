import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Box, Heading, Text, Button } from "@chakra-ui/react";
import { useAuth, Permission } from "@/hooks/";

/**
 * Options for the withPermission HOC
 */
interface WithPermissionOptions {
  /** Required permission to access the component */
  requiredPermission: Permission;

  /** Fallback component to show when unauthorized */
  fallback?: React.ReactNode;

  /** Where to redirect unauthorized users (if not using fallback) */
  redirectTo?: string;

  /** Show loading state while checking auth */
  showLoading?: boolean;
}

/**
 * Default unauthorized component
 */
const DefaultUnauthorized: React.FC<{ redirectTo?: string }> = ({
  redirectTo,
}) => {
  const router = useRouter();

  return (
    <Box p={8} textAlign="center">
      <Heading size="lg" mb={4} color="red.500">
        Access Denied
      </Heading>
      <Text mb={6}>
        You don&apos;t have permission to access this resource.
      </Text>
      {redirectTo && (
        <Button colorScheme="blue" onClick={() => router.push(redirectTo)}>
          Go Back
        </Button>
      )}
    </Box>
  );
};

/**
 * Higher-order component that restricts access based on permissions
 *
 * @param Component The component to protect
 * @param options Permission options
 */
export function withPermission<P extends object>(
  Component: React.ComponentType<P>,
  options: WithPermissionOptions
) {
  const {
    requiredPermission,
    fallback,
    redirectTo = "/",
    showLoading = true,
  } = options;

  // The wrapped component with permission check
  const WrappedComponent: React.FC<P> = (props) => {
    const { isAuthenticated, hasPermission, isLoading } = useAuth();
    const router = useRouter();

    // Handle redirects in useEffect to ensure they only happen client-side
    useEffect(() => {
      // Check if user is authenticated and has permission
      const hasAccess = isAuthenticated && hasPermission(requiredPermission);

      // Only redirect if user doesn't have access and redirectTo is set
      if (!hasAccess && redirectTo && !fallback) {
        router.push(redirectTo);
      }
    }, [isAuthenticated, hasPermission, router]);

    // Handle loading state
    if (showLoading && isLoading) {
      return (
        <Box p={8} textAlign="center">
          <Text>Checking permissions...</Text>
        </Box>
      );
    }

    // Check if user is authenticated and has permission
    const hasAccess = isAuthenticated && hasPermission(requiredPermission);

    // If no access, show fallback or unauthorized message
    if (!hasAccess) {
      // If fallback is provided, show it
      if (fallback) {
        return <>{fallback}</>;
      }

      // Default unauthorized component (redirect happens in useEffect)
      return <DefaultUnauthorized redirectTo={redirectTo} />;
    }

    // User has permission, render the component
    return <Component {...props} />;
  };

  // Set display name for debugging
  const displayName = Component.displayName || Component.name || "Component";
  WrappedComponent.displayName = `withPermission(${displayName})`;

  return WrappedComponent;
}

export default withPermission;
