import {
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Text,
  useColorModeValue,
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
  const textColor = useColorModeValue("black", "white");
  const modalBgColor = useColorModeValue("gray.100", "gray.800");

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
      <ModalContent bg={modalBgColor} color={textColor}>
        <ModalHeader>
          <Text fontSize="2xl" fontWeight="medium">
            {title}
          </Text>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody padding={6}>{children}</ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default BaseModal;
