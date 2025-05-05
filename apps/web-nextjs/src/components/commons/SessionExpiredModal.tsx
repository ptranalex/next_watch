import React, { useEffect, useState } from "react";
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  useDisclosure,
  Text,
  Box,
  Icon,
} from "@chakra-ui/react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks";
import { HiExclamationCircle } from "react-icons/hi";
import LoginModal from "../auth/LoginModal";

/**
 * A modal that appears when the user's session has expired
 * It automatically listens for auth errors and displays when needed
 */
const SessionExpiredModal: React.FC = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { error, clearError } = useAuth();
  const router = useRouter();
  const [showLoginModal, setShowLoginModal] = useState(false);

  // Check for session expiration errors
  useEffect(() => {
    if (error && error.includes("session has expired")) {
      onOpen();
    }
  }, [error, onOpen]);

  // Handle login button click
  const handleLogin = () => {
    clearError();
    onClose();
    setShowLoginModal(true);
  };

  const handleLoginModalClose = () => {
    setShowLoginModal(false);
  };

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        isCentered
        closeOnOverlayClick={false}
      >
        <ModalOverlay />
        <ModalContent>
          <ModalHeader display="flex" alignItems="center">
            <Icon
              as={HiExclamationCircle}
              color="orange.500"
              boxSize={6}
              mr={2}
            />
            Session Expired
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Text>
              Your session has expired. Please log in again to continue using
              the application.
            </Text>
            <Box mt={4} fontStyle="italic" fontSize="sm" color="gray.500">
              Any unsaved changes may be lost.
            </Box>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Close
            </Button>
            <Button colorScheme="blue" onClick={handleLogin}>
              Log In Again
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Login Modal */}
      <LoginModal isOpen={showLoginModal} onClose={handleLoginModalClose} />
    </>
  );
};

export default SessionExpiredModal;
