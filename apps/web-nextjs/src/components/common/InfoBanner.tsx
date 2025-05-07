import React from "react";
import { Box, Flex, Icon, Text, CloseButton } from "@chakra-ui/react";
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

const variantStyles: Record<
  InfoBannerVariant,
  {
    bg: string;
    color: string;
    icon: IconType;
  }
> = {
  info: {
    bg: "blue.50",
    color: "blue.700",
    icon: HiInformationCircle,
  },
  warning: {
    bg: "yellow.50",
    color: "yellow.800",
    icon: HiExclamationTriangle,
  },
  error: {
    bg: "red.50",
    color: "red.700",
    icon: HiXCircle,
  },
  success: {
    bg: "green.50",
    color: "green.700",
    icon: HiCheckCircle,
  },
};

const InfoBanner: React.FC<InfoBannerProps> = ({
  variant = "info",
  children,
  icon,
  onClose,
}) => {
  const { bg, color, icon: DefaultIcon } = variantStyles[variant];
  const BannerIcon = icon || DefaultIcon;

  return (
    <Box
      bg="blue.50"
      color="blue.800"
      p={4}
      borderRadius="md"
      border="1px solid"
      borderColor="blue.100"
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
            color="blue.800"
            _hover={{ bg: "blue.100" }}
          />
        )}
      </Flex>
    </Box>
  );
};

export default InfoBanner;
