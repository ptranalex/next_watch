import { Box, Button, Flex, Icon, Text } from "@chakra-ui/react";
import React from "react";
import { IconType } from "react-icons";

interface BaseCTAProps {
  onClick?: () => void;
  icon?: IconType;
  isLoading?: boolean;
  width?: string;
  type?: "button" | "submit" | "reset";
  size?: "sm" | "md" | "lg";
  isDisabled?: boolean;
}

interface PrimaryCTAProps extends BaseCTAProps {
  children: React.ReactNode;
  variant?: "solid" | "outline" | "ghost" | "link";
}

interface SecondaryCTAProps extends BaseCTAProps {
  children: React.ReactNode;
  variant?: "solid" | "outline" | "ghost" | "link";
}

interface TertiaryCTAProps extends BaseCTAProps {
  children: React.ReactNode;
  variant?: "solid" | "outline" | "ghost" | "link";
}

interface DividerProps {
  text?: string;
}

/**
 * PrimaryCTA - Primary call-to-action button using brand primary colors
 */
export const PrimaryCTA: React.FC<PrimaryCTAProps> = ({
  children,
  onClick,
  icon,
  isLoading,
  width = "100%",
  type = "button",
  size = "md",
  isDisabled,
  variant = "solid",
}) => {
  return (
    <Button
      width={width}
      bg="colors.primary"
      color="text.inverse"
      _hover={{ bg: "colors.primary.darker" }}
      _active={{ bg: "colors.primary.darker" }}
      variant={variant}
      leftIcon={
        icon ? (
          <Icon as={icon} fontSize={size === "lg" ? "1.75rem" : "1.5rem"} />
        ) : undefined
      }
      justifyContent="left"
      onClick={onClick}
      isLoading={isLoading}
      type={type}
      size={size}
      isDisabled={isDisabled}
    >
      {children}
    </Button>
  );
};

/**
 * SecondaryCTA - Secondary call-to-action button using brand secondary colors
 */
export const SecondaryCTA: React.FC<SecondaryCTAProps> = ({
  children,
  onClick,
  icon,
  isLoading,
  width = "100%",
  type = "button",
  size = "md",
  isDisabled,
  variant = "solid",
}) => {
  return (
    <Button
      width={width}
      bg="colors.secondary"
      color="text.inverse"
      _hover={{ bg: "colors.secondary.darker" }}
      _active={{ bg: "colors.secondary.darker" }}
      variant={variant}
      leftIcon={
        icon ? (
          <Icon as={icon} fontSize={size === "lg" ? "1.75rem" : "1.5rem"} />
        ) : undefined
      }
      justifyContent="left"
      onClick={onClick}
      isLoading={isLoading}
      type={type}
      size={size}
      isDisabled={isDisabled}
    >
      {children}
    </Button>
  );
};

/**
 * TertiaryCTA - Tertiary call-to-action button (ghost style)
 */
export const TertiaryCTA: React.FC<TertiaryCTAProps> = ({
  children,
  onClick,
  icon,
  isLoading,
  width = "100%",
  type = "button",
  size = "md",
  isDisabled,
  variant = "ghost",
}) => {
  return (
    <Button
      width={width}
      color="text.tertiary"
      _hover={{ bg: "bg.tertiary" }}
      variant={variant}
      leftIcon={
        icon ? (
          <Icon as={icon} fontSize={size === "lg" ? "1.75rem" : "1.5rem"} />
        ) : undefined
      }
      justifyContent="left"
      onClick={onClick}
      isLoading={isLoading}
      type={type}
      size={size}
      isDisabled={isDisabled}
    >
      {children}
    </Button>
  );
};

export const Divider: React.FC<DividerProps> = ({ text }) => {
  if (!text) {
    return <Box width="100%" height="1px" bg="text.tertiary" my={4} />;
  }

  return (
    <Flex align="center" width="100%" my={4}>
      <Box flex="1" height="1px" bg="text.tertiary" />
      <Text mx={3} fontSize="sm" color="text.secondary">
        {text}
      </Text>
      <Box flex="1" height="1px" bg="text.tertiary" />
    </Flex>
  );
};
