import {
  Avatar,
  Button,
  Divider,
  Flex,
  HStack,
  Heading,
  Icon,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Stack,
  Text,
  VStack,
  useColorModeValue,
  useToast,
} from "@chakra-ui/react";
import React, { useState } from "react";
import { HiArrowRightOnRectangle, HiOutlineArrowUpTray } from "react-icons/hi2";
import { useAuth } from "@/hooks";
import { useRouter } from "next/navigation";
import ImportNetflixHistoryModal from "./ImportNetflixHistoryModal";

interface ProfileModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const ProfileModal: React.FC<ProfileModalProps> = ({ isOpen, onClose }) => {
  const { user, logout } = useAuth();
  const router = useRouter();
  const toast = useToast();
  const textColor = useColorModeValue("black", "white");
  const modalBgColor = useColorModeValue("gray.100", "gray.800");
  const [isImportModalOpen, setIsImportModalOpen] = useState(false);

  const handleLogout = () => {
    logout();
    onClose();
    toast({
      title: "Signed out successfully.",
      description: "You have been signed out.",
      status: "info",
      duration: 4000,
      isClosable: true,
    });
    router.push("/");
  };

  const openImportModal = () => {
    onClose(); // Close profile modal first
    setIsImportModalOpen(true);
  };

  const closeImportModal = () => {
    setIsImportModalOpen(false);
  };

  if (!user) {
    return null;
  }

  return (
    <>
      <Modal isCentered isOpen={isOpen} onClose={onClose}>
        <ModalOverlay
          bg="blackAlpha.300"
          backdropFilter="auto"
          backdropBlur="4px"
        />
        <ModalContent bg={modalBgColor} color={textColor}>
          <ModalHeader>
            <Text fontSize="2xl">Profile</Text>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody padding={6}>
            <Stack spacing={4}>
              <Flex justifyContent="center">
                <Avatar size="xl" name={user.username || user.email} mb={4} />
              </Flex>

              <VStack align="center" spacing={1}>
                <Heading as="h3" size="md">
                  {user.username || "User"}
                </Heading>
                <Text color="gray.500">{user.email}</Text>
              </VStack>

              <Divider />

              <Heading as="h4" size="sm" alignSelf="center" mb={2}>
                Watch History
              </Heading>

              <Button
                colorScheme="teal"
                leftIcon={<Icon as={HiOutlineArrowUpTray} />}
                onClick={openImportModal}
                width="100%"
                justifyContent="left"
              >
                Import Netflix History
              </Button>

              <Divider />

              <Button
                colorScheme="red"
                variant="outline"
                leftIcon={<Icon as={HiArrowRightOnRectangle} />}
                onClick={handleLogout}
                width="100%"
                justifyContent="left"
              >
                Logout
              </Button>
            </Stack>
          </ModalBody>
        </ModalContent>
      </Modal>

      <ImportNetflixHistoryModal
        isOpen={isImportModalOpen}
        onClose={closeImportModal}
      />
    </>
  );
};

export default ProfileModal;
