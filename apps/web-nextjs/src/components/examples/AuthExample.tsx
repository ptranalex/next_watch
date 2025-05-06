import React from "react";
import {
  Box,
  Button,
  Heading,
  Text,
  VStack,
  Badge,
  Divider,
} from "@chakra-ui/react";
import { useAuth, useCurrentUser, usePermission, Permission } from "@/hooks";

/**
 * Example component showing how to use the auth hooks
 */
const AuthExample: React.FC = () => {
  // Get full auth capabilities
  const { login, logout, isAuthenticated, isAdmin, hasPermission } = useAuth();

  // Get just the current user
  const currentUser = useCurrentUser();

  // Check a specific permission
  const { isAuthorized: canEditMovies } = usePermission("movies:write");

  // Example login handler
  const handleLogin = () => {
    login("user@example.com", "password123");
  };

  // Example permission check
  const checkSpecificPermission = (permission: Permission) => {
    return hasPermission(permission)
      ? "✅ Has permission"
      : "❌ Does not have permission";
  };

  return (
    <Box p={5} borderWidth={1} borderRadius="md" shadow="md">
      <Heading size="md" mb={4}>
        Auth Hooks Example
      </Heading>

      {/* Authentication status */}
      <Text fontWeight="bold">
        Status:{" "}
        {isAuthenticated ? (
          <Badge colorScheme="green">Authenticated</Badge>
        ) : (
          <Badge colorScheme="red">Not Authenticated</Badge>
        )}
      </Text>

      {/* Login/Logout buttons */}
      <Box my={4}>
        {isAuthenticated ? (
          <Button colorScheme="red" onClick={logout}>
            Log Out
          </Button>
        ) : (
          <Button colorScheme="blue" onClick={handleLogin}>
            Log In
          </Button>
        )}
      </Box>

      <Divider my={4} />

      {/* Current user information */}
      {currentUser && (
        <VStack align="start" spacing={2} mb={4}>
          <Heading size="sm">Current User:</Heading>
          <Text>Display Name: {currentUser.displayName}</Text>
          <Text>Email: {currentUser.email}</Text>
          <Text>
            Role: <Badge>{currentUser.role}</Badge>
          </Text>
          <Text>Admin Access: {isAdmin ? "Yes" : "No"}</Text>
        </VStack>
      )}

      <Divider my={4} />

      {/* Permission checks */}
      <VStack align="start" spacing={2}>
        <Heading size="sm">Permissions:</Heading>
        <Text>Can Edit Movies: {canEditMovies ? "Yes" : "No"}</Text>

        <Text>movies:read: {checkSpecificPermission("movies:read")}</Text>
        <Text>movies:write: {checkSpecificPermission("movies:write")}</Text>
        <Text>admin:access: {checkSpecificPermission("admin:access")}</Text>
      </VStack>
    </Box>
  );
};

export default AuthExample;
