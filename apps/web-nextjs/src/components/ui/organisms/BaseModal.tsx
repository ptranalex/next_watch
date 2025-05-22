import {
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
} from "@chakra-ui/react";
import React from "react";

interface BaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: "xs" | "sm" | "md" | "lg" | "xl" | "full";
  isCentered?: boolean;
}

const BaseModal: React.FC<BaseModalProps> = ({
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
        <ModalHeader fontSize="2xl" fontWeight="medium">
          {title}
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody padding={6}>{children}</ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default BaseModal;
