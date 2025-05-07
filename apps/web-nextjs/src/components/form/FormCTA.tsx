import { Button, Center, Text, Icon, Flex, Box } from "@chakra-ui/react";
import React from "react";
import { IconType } from "react-icons";

interface BaseCTAProps {
  onClick?: () => void;
  icon?: IconType;
  isLoading?: boolean;
  width?: string;
  type?: "button" | "submit" | "reset";
  variant?: string;
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

export const PrimaryCTA: React.FC<PrimaryCTAProps> = ({
  children,
  onClick,
  icon,
  isLoading,
  width = "100%",
  type = "button",
  variant,
}) => {
  return (
    <Button
      width={width}
      colorScheme="blue"
      leftIcon={icon ? <Icon as={icon} fontSize="1.5rem" /> : undefined}
      justifyContent="left"
      onClick={onClick}
      isLoading={isLoading}
      type={type}
      variant={variant}
    >
      {children}
    </Button>
  );
};

export const SecondaryCTA: React.FC<SecondaryCTAProps> = ({
  children,
  onClick,
  icon,
  isLoading,
  width = "100%",
  type = "button",
  variant,
}) => {
  return (
    <Button
      width={width}
      colorScheme="teal"
      leftIcon={icon ? <Icon as={icon} fontSize="1.5rem" /> : undefined}
      justifyContent="left"
      onClick={onClick}
      isLoading={isLoading}
      type={type}
      variant={variant}
    >
      {children}
    </Button>
  );
};

export const TertiaryCTA: React.FC<TertiaryCTAProps> = ({
  children,
  onClick,
  icon,
  isLoading,
  width = "100%",
  type = "button",
}) => {
  return (
    <Button
      width={width}
      variant="ghost"
      leftIcon={icon ? <Icon as={icon} fontSize="1.5rem" /> : undefined}
      justifyContent="left"
      onClick={onClick}
      isLoading={isLoading}
      type={type}
    >
      {children}
    </Button>
  );
};

export const Divider: React.FC<DividerProps> = ({ text }) => {
  if (!text) {
    return <Box width="100%" height="1px" bg="gray.600" my={4} />;
  }

  return (
    <Flex align="center" width="100%" my={4}>
      <Box flex="1" height="1px" bg="gray.600" />
      <Text mx={3} fontSize="sm" color="gray.400">
        {text}
      </Text>
      <Box flex="1" height="1px" bg="gray.600" />
    </Flex>
  );
};
