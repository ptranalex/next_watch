"use client";

import { ReactElement } from "react";
import {
  IconButton,
  IconButtonProps,
  Tooltip,
  useColorModeValue,
} from "@chakra-ui/react";

interface ToggleIconButtonProps extends Omit<IconButtonProps, "aria-label"> {
  isActive: boolean;
  activeIcon: ReactElement;
  inactiveIcon: ReactElement;
  activeColor?: string;
  inactiveColor?: string;
  tooltipLabel?: string;
  "aria-label": string;
  onClick: () => void;
}

export default function ToggleIconButton({
  isActive,
  activeIcon,
  inactiveIcon,
  activeColor = "blue.500",
  inactiveColor,
  tooltipLabel,
  "aria-label": ariaLabel,
  onClick,
  ...rest
}: ToggleIconButtonProps) {
  // Default inactive color based on color mode if not specified
  const defaultInactiveColor = useColorModeValue("gray.600", "gray.400");
  const finalInactiveColor = inactiveColor || defaultInactiveColor;

  const button = (
    <IconButton
      icon={isActive ? activeIcon : inactiveIcon}
      color={isActive ? activeColor : finalInactiveColor}
      onClick={onClick}
      aria-label={ariaLabel}
      {...rest}
    />
  );

  if (tooltipLabel) {
    return <Tooltip label={tooltipLabel}>{button}</Tooltip>;
  }

  return button;
}
