"use client";

import React, { ReactNode } from "react";
import { useProtectedRoute } from "@/hooks";
import { Spinner, Center, VStack, Text } from "@chakra-ui/react";

interface ProtectedRouteProps {
  children: ReactNode;
  redirectUrl?: string;
  requiredPermission?: string;
  loadingComponent?: ReactNode;
}

/**
 * Component that protects routes requiring authentication
 * Use this to wrap pages that should only be accessible to authenticated users
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  redirectUrl,
  requiredPermission,
  loadingComponent,
}) => {
  const { isLoading, isAuthorized } = useProtectedRoute({
    redirectUrl,
    requiredPermission,
  });

  // Show loading state
  if (isLoading) {
    if (loadingComponent) {
      return <>{loadingComponent}</>;
    }

    return (
      <Center h="100vh">
        <VStack spacing={4}>
          <Spinner size="xl" color="colors.primary" thickness="4px" />
          <Text>Checking authorization...</Text>
        </VStack>
      </Center>
    );
  }

  // User is not authorized but useProtectedRoute will handle redirect
  // Just render nothing until redirect happens
  if (!isAuthorized) {
    return null;
  }

  // User is authorized, render the protected content
  return <>{children}</>;
};

export default ProtectedRoute;
