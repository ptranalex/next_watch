import {
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
} from "@chakra-ui/react";
import React from "react";
import type { BaseModalProps } from "./types";

/**
 * Extended BaseModal Props
 *
 * Extends the shared BaseModalProps with additional modal-specific options
 */
interface ExtendedBaseModalProps extends BaseModalProps {
  isCentered?: boolean;
}

/**
 * BaseModal - A foundational modal component
 *
 * @param isOpen - Whether the modal is open
 * @param onClose - Callback to close the modal
 * @param title - Modal title (optional)
 * @param children - Modal content
 * @param size - Modal size variant
 * @param isCentered - Whether to center the modal vertically
 */
const BaseModal: React.FC<ExtendedBaseModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = "md",
  isCentered = true,
}) => {
  return (
    <Modal
      isCentered={isCentered}
      isOpen={isOpen}
      onClose={onClose}
      size={size}
    >
      <ModalOverlay
        bg="blackAlpha.700"
        backdropFilter="blur(8px) hue-rotate(15deg)"
      />
      <ModalContent bg="bg.secondary" color="text.primary">
        {title && (
          <ModalHeader fontSize="2xl" fontWeight="medium">
            {title}
          </ModalHeader>
        )}
        <ModalCloseButton />
        <ModalBody padding={6}>{children}</ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default BaseModal;
