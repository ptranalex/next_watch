"use client";

import React from "react";
import { useProtectedRoute } from "@/services/hooks";
import { Spinner, Center, VStack, Text } from "@chakra-ui/react";
import type { ProtectedRouteProps } from "./types";

/**
 * Component that protects routes requiring authentication
 * Use this to wrap pages that should only be accessible to authenticated users
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireAuth = true,
  requiredRoles = [],
  fallback,
}) => {
  const { isLoading, isAuthorized } = useProtectedRoute({
    redirectUrl: undefined, // Can be enhanced to support custom redirect URLs
    requiredPermission: requiredRoles[0], // For now, use first role as permission
  });

  // Show loading state
  if (isLoading) {
    if (fallback) {
      return <>{fallback}</>;
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
  if (requireAuth && !isAuthorized) {
    return null;
  }

  // User is authorized, render the protected content
  return <>{children}</>;
};

export default ProtectedRoute;
