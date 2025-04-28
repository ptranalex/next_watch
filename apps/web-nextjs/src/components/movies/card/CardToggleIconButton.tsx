"use client";

import { ReactElement } from "react";
import { IconButtonProps } from "@chakra-ui/react";
import ToggleIconButton from "@/src/components/common/ToggleIconButton";

interface CardToggleIconButtonProps
  extends Omit<IconButtonProps, "aria-label"> {
  isActive: boolean;
  activeIcon: ReactElement;
  inactiveIcon: ReactElement;
  activeColor?: string;
  inactiveColor?: string;
  tooltipLabel?: string;
  "aria-label": string;
  onClick: () => void;
}

export default function CardToggleIconButton({
  size = "sm",
  variant = "ghost",
  borderRadius = "full",
  ...props
}: CardToggleIconButtonProps) {
  return (
    <ToggleIconButton
      size={size}
      variant={variant}
      borderRadius={borderRadius}
      _hover={{ bg: "rgba(0, 0, 0, 0.1)" }}
      {...props}
    />
  );
}
