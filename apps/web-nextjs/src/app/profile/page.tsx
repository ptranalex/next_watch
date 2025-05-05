"use client";

import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  Avatar,
  Button,
  useColorModeValue,
  Divider,
  Flex,
} from "@chakra-ui/react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks";
import ProtectedRoute from "@/components/auth/ProtectedRoute";

export default function ProfilePage() {
  const router = useRouter();
  const bgColor = useColorModeValue("gray.50", "gray.900");
  const cardBgColor = useColorModeValue("white", "gray.800");

  return (
    <ProtectedRoute>
      <ProfileContent />
    </ProtectedRoute>
  );
}

// Separate component for the profile content
function ProfileContent() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const bgColor = useColorModeValue("gray.50", "gray.900");
  const cardBgColor = useColorModeValue("white", "gray.800");

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  if (!user) {
    return null; // This shouldn't happen due to ProtectedRoute, but just in case
  }

  return (
    <Box bg={bgColor} minH="calc(100vh - 60px)" py={10}>
      <Container maxW="container.md">
        <VStack
          spacing={8}
          align="stretch"
          bg={cardBgColor}
          p={8}
          borderRadius="lg"
          boxShadow="md"
        >
          <Flex justifyContent="center">
            <Avatar size="2xl" name={user.username || user.email} mb={4} />
          </Flex>

          <VStack align="center" spacing={1}>
            <Heading as="h1" size="xl">
              {user.username || "User"}
            </Heading>
            <Text color="gray.500">{user.email}</Text>
          </VStack>

          <Divider />

          <Button
            colorScheme="red"
            variant="outline"
            onClick={handleLogout}
            alignSelf="center"
          >
            Logout
          </Button>
        </VStack>
      </Container>
    </Box>
  );
}
