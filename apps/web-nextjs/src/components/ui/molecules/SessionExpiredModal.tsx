"use client";

import React from "react";
import { LoginModal } from "@/components/features/auth";
import { useAuth } from "@/services/hooks";
import {
  Box,
  Button,
  Icon,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Text,
  useDisclosure,
} from "@chakra-ui/react";
import { HiExclamationCircle } from "react-icons/hi";

// The definitive session expired messages that should trigger this modal
// These should ONLY be set when automatic recovery has already failed
const DEFINITIVE_SESSION_ERRORS = [
  "Your session has expired. Please log in again.",
  "Session expired",
];

/**
 * A simple modal that appears when the user's session has expired and
 * automatic recovery attempts have failed.
 * This component ONLY handles UI display and doesn't attempt recovery.
 */
const SessionExpiredModal: React.FC = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { error, clearError } = useAuth();
  const [showLoginModal, setShowLoginModal] = React.useState(false);

  // Only show for definitive session expired errors
  React.useEffect(() => {
    if (error && DEFINITIVE_SESSION_ERRORS.some((msg) => error.includes(msg))) {
      onOpen();
    }
  }, [error, onOpen]);

  // Handle login button click
  const handleLogin = () => {
    clearError();
    onClose();
    setShowLoginModal(true);
  };

  const handleClose = () => {
    clearError();
    onClose();
  };

  const handleLoginModalClose = () => {
    setShowLoginModal(false);
  };

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={handleClose}
        isCentered
        closeOnOverlayClick={false}
      >
        <ModalOverlay backdropFilter="blur(4px)" />
        <ModalContent>
          <ModalHeader display="flex" alignItems="center">
            <Icon
              as={HiExclamationCircle}
              color="feedback.warning"
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
            <Box mt={4} fontStyle="italic" fontSize="sm" color="text.tertiary">
              Any unsaved changes may be lost.
            </Box>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={handleClose}>
              Close
            </Button>
            <Button
              bg="colors.primary"
              color="text.inverse"
              _hover={{ bg: "colors.primary.darker" }}
              onClick={handleLogin}
            >
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
