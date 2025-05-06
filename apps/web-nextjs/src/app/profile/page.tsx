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
  Icon,
  HStack,
} from "@chakra-ui/react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks";
import ProtectedRoute from "@/components/auth/ProtectedRoute";
import { useState } from "react";
import ImportNetflixHistoryModal from "@/components/profile/ImportNetflixHistoryModal";
import { HiFilm, HiOutlineArrowUpTray } from "react-icons/hi2";

export default function ProfilePage() {
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
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  const openImportModal = () => {
    setIsImportModalOpen(true);
  };

  const closeImportModal = () => {
    setIsImportModalOpen(false);
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
}
