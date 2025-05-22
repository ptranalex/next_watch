import React from "react";
import {
  Box,
  Flex,
  Icon,
  Text,
  CloseButton,
  useColorModeValue,
} from "@chakra-ui/react";
import {
  HiInformationCircle,
  HiExclamationTriangle,
  HiCheckCircle,
  HiXCircle,
} from "react-icons/hi2";
import { IconType } from "react-icons";

export type InfoBannerVariant = "info" | "warning" | "error" | "success";

interface InfoBannerProps {
  variant?: InfoBannerVariant;
  children: React.ReactNode;
  icon?: IconType;
  onClose?: () => void;
}

// Define variant icons outside component as they don't depend on color mode
const variantIcons: Record<InfoBannerVariant, IconType> = {
  info: HiInformationCircle,
  warning: HiExclamationTriangle,
  error: HiXCircle,
  success: HiCheckCircle,
};

const InfoBanner: React.FC<InfoBannerProps> = ({
  variant = "info",
  children,
  icon,
  onClose,
}) => {
  // Define variant styles inside component to use hooks properly
  const variantStyles = {
    info: {
      bg: useColorModeValue("blue.50", "blue.900"),
      color: useColorModeValue("blue.700", "blue.200"),
      borderColor: useColorModeValue("blue.100", "blue.800"),
      hoverBg: useColorModeValue("blue.100", "blue.800"),
    },
    warning: {
      bg: useColorModeValue("yellow.50", "yellow.900"),
      color: useColorModeValue("yellow.800", "yellow.200"),
      borderColor: useColorModeValue("yellow.100", "yellow.800"),
      hoverBg: useColorModeValue("yellow.100", "yellow.800"),
    },
    error: {
      bg: useColorModeValue("red.50", "red.900"),
      color: useColorModeValue("red.700", "red.200"),
      borderColor: useColorModeValue("red.100", "red.800"),
      hoverBg: useColorModeValue("red.100", "red.800"),
    },
    success: {
      bg: useColorModeValue("green.50", "green.900"),
      color: useColorModeValue("green.700", "green.200"),
      borderColor: useColorModeValue("green.100", "green.800"),
      hoverBg: useColorModeValue("green.100", "green.800"),
    },
  };

  const styles = variantStyles[variant];
  const BannerIcon = icon || variantIcons[variant];

  return (
    <Box
      bg={styles.bg}
      color={styles.color}
      p={4}
      borderRadius="md"
      border="1px solid"
      borderColor={styles.borderColor}
      position="relative"
      role="alert"
    >
      <Flex alignItems="start">
        <Icon as={BannerIcon} boxSize={5} mr={3} mt={1} />
        <Text fontSize="sm" lineHeight="1.5" flex="1">
          {children}
        </Text>
        {onClose && (
          <CloseButton
            size="sm"
            onClick={onClose}
            position="absolute"
            top={2}
            right={2}
            color={styles.color}
            _hover={{ bg: styles.hoverBg }}
          />
        )}
      </Flex>
    </Box>
  );
};

export default InfoBanner;
