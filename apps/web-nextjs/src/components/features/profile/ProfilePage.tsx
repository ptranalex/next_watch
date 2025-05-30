"use client";

// 1. React and core libraries
import { useEffect, useState, memo, useCallback } from "react";
import { useRouter } from "next/navigation";

// 2. Third-party libraries (Chakra UI, etc.)
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
  Icon,
  HStack,
} from "@chakra-ui/react";
import { HiOutlineArrowUpTray } from "react-icons/hi2";

// 3. Internal services and APIs
import { useAuth } from "@/services/hooks";

// 4. Local components
import { ProtectedRoute } from "@/components/features/auth";
import ImportNetflixHistoryModal from "./ImportNetflixHistoryModal";

// 5. Utilities
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("ProfilePage");

/**
 * ProfilePage component - User profile page with authentication protection
 *
 * This is a feature-level component that contains all the business logic
 * for displaying user profile information, handling authentication,
 * managing watch history, and account actions.
 *
 * Provides user information display, watch history management, and account actions.
 * Wrapped in ProtectedRoute to ensure only authenticated users can access.
 */
const ProfilePage: React.FC = () => {
  // Log component initialization
  logger.debug("ProfilePage feature component initializing");

  return (
    <ProtectedRoute>
      <MemoizedProfileContent />
    </ProtectedRoute>
  );
};

export default ProfilePage;

/**
 * ProfileContent component - Main profile content implementation
 *
 * Displays user information, watch history controls, and account management.
 * Separated from ProfilePage to isolate protected content logic.
 */
const ProfileContent: React.FC = () => {
  // Create specific logger for profile content
  const contentLogger = createLogger("ProfileContent");

  const { user, logout } = useAuth();
  const router = useRouter();
  const bgColor = useColorModeValue("gray.50", "gray.900");
  const cardBgColor = useColorModeValue("white", "gray.800");
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);

  // Log when user data is loaded
  useEffect(() => {
    if (user) {
      contentLogger.info(`Profile loaded for user: ${user.email}`);
    }
  }, [user, contentLogger]);

  const handleLogout = useCallback(() => {
    contentLogger.info("User initiated logout from profile page");
    logout();
    router.push("/");
  }, [contentLogger, logout, router]);

  const openImportModal = useCallback(() => {
    contentLogger.info("User opened Netflix history import modal");
    setIsImportModalOpen(true);
  }, [contentLogger]);

  const closeImportModal = useCallback(() => {
    contentLogger.debug("User closed Netflix history import modal");
    setIsImportModalOpen(false);
  }, [contentLogger]);

  if (!user) {
    contentLogger.warn("ProfileContent rendered without user data");
    return null; // This shouldn't happen due to ProtectedRoute, but just in case
  }

  return (
    <Box bg={bgColor} minH="calc(100vh - 60px)" py={{ base: 4, md: 10 }}>
      <Container maxW={{ base: "container.sm", md: "container.md" }}>
        <VStack
          spacing={{ base: 6, md: 8 }}
          align="stretch"
          bg={cardBgColor}
          p={{ base: 6, md: 8 }}
          borderRadius="lg"
          boxShadow="md"
        >
          <Flex justifyContent="center">
            <Avatar
              size={{ base: "xl", md: "2xl" }}
              name={user.username || user.email}
              mb={4}
            />
          </Flex>

          <VStack align="center" spacing={1}>
            <Heading as="h1" size="xl">
              {user.username || "User"}
            </Heading>
            <Text color="gray.500">{user.email}</Text>
          </VStack>

          <Divider />

          <Heading as="h3" size="md" alignSelf="center" mb={2}>
            Your Watch History
          </Heading>

          <HStack justifyContent="center" spacing={4}>
            <Button
              colorScheme="teal"
              leftIcon={<Icon as={HiOutlineArrowUpTray} />}
              onClick={openImportModal}
            >
              Import Netflix History
            </Button>
          </HStack>

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

      <ImportNetflixHistoryModal
        isOpen={isImportModalOpen}
        onClose={closeImportModal}
      />
    </Box>
  );
};

// Memoize the ProfileContent component for performance
const MemoizedProfileContent = memo(ProfileContent);
