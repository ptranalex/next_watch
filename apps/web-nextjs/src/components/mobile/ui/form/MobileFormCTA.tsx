import { Box, Button, Flex, Icon, Text } from "@chakra-ui/react";
import React from "react";
import { IconType } from "react-icons";
import { createLogger } from "@/utils/logging";

const logger = createLogger("MobileFormCTA");

interface BaseCTAProps {
  onClick?: () => void;
  icon?: IconType;
  isLoading?: boolean;
  width?: string;
  type?: "button" | "submit" | "reset";
  variant?: string;
  enableHaptics?: boolean;
}

interface PrimaryCTAProps extends Omit<BaseCTAProps, "colorScheme"> {
  children: React.ReactNode;
}

interface SecondaryCTAProps extends Omit<BaseCTAProps, "colorScheme"> {
  children: React.ReactNode;
}

interface TertiaryCTAProps extends Omit<BaseCTAProps, "variant"> {
  children: React.ReactNode;
}

interface DividerProps {
  text?: string;
}

// Helper function for haptic feedback
const triggerHaptics = (pattern: number | number[] = 50) => {
  if (window.navigator && "vibrate" in window.navigator) {
    try {
      window.navigator.vibrate(pattern);
    } catch (e) {
      logger.warn("Vibration not supported", e);
    }
  }
};

export const MobilePrimaryCTA: React.FC<PrimaryCTAProps> = ({
  children,
  onClick,
  icon,
  isLoading,
  width = "100%",
  type = "button",
  variant,
  enableHaptics = true,
}) => {
  const handleClick = () => {
    if (enableHaptics) {
      triggerHaptics(50);
    }
    onClick?.();
  };

  return (
    <Button
      width={width}
      colorScheme="blue"
      leftIcon={icon ? <Icon as={icon} fontSize="1.5rem" /> : undefined}
      justifyContent="center" // Center for mobile
      onClick={handleClick}
      isLoading={isLoading}
      type={type}
      variant={variant}
      size="lg" // Larger size for touch targets
      height="56px" // Fixed height for better touch area
      borderRadius="md"
      fontSize="md"
      fontWeight="semibold"
      boxShadow="sm"
    >
      {children}
    </Button>
  );
};

export const MobileSecondaryCTA: React.FC<SecondaryCTAProps> = ({
  children,
  onClick,
  icon,
  isLoading,
  width = "100%",
  type = "button",
  variant,
  enableHaptics = true,
}) => {
  const handleClick = () => {
    if (enableHaptics) {
      triggerHaptics(30);
    }
    onClick?.();
  };

  return (
    <Button
      width={width}
      colorScheme="teal"
      leftIcon={icon ? <Icon as={icon} fontSize="1.5rem" /> : undefined}
      justifyContent="center" // Center for mobile
      onClick={handleClick}
      isLoading={isLoading}
      type={type}
      variant={variant || "outline"}
      size="lg"
      height="56px"
      borderRadius="md"
      fontSize="md"
    >
      {children}
    </Button>
  );
};

export const MobileTertiaryCTA: React.FC<TertiaryCTAProps> = ({
  children,
  onClick,
  icon,
  isLoading,
  width = "100%",
  type = "button",
  enableHaptics = true,
}) => {
  const handleClick = () => {
    if (enableHaptics) {
      triggerHaptics(20);
    }
    onClick?.();
  };

  return (
    <Button
      width={width}
      variant="ghost"
      leftIcon={icon ? <Icon as={icon} fontSize="1.5rem" /> : undefined}
      justifyContent="center" // Center for mobile
      onClick={handleClick}
      isLoading={isLoading}
      type={type}
      size="md"
      height="48px"
      borderRadius="md"
      fontSize="md"
    >
      {children}
    </Button>
  );
};

export const MobileDivider: React.FC<DividerProps> = ({ text }) => {
  if (!text) {
    return <Box width="100%" height="1px" bg="gray.600" my={5} />; // Increased margin
  }

  return (
    <Flex align="center" width="100%" my={5}>
      {" "}
      {/* Increased margin */}
      <Box flex="1" height="1px" bg="gray.600" />
      <Text mx={3} fontSize="sm" color="gray.400" fontWeight="medium">
        {text}
      </Text>
      <Box flex="1" height="1px" bg="gray.600" />
    </Flex>
  );
};

// Export all components
export const MobileFormCTA = {
  Primary: MobilePrimaryCTA,
  Secondary: MobileSecondaryCTA,
  Tertiary: MobileTertiaryCTA,
  Divider: MobileDivider,
};

export default MobileFormCTA;
