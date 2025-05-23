import { IconButton } from "@chakra-ui/react";
import React, { useState } from "react";
import { TiMinus, TiPlus } from "react-icons/ti";
import type { BaseToggleProps, ComponentSize } from "./types";

/**
 * ToggleIconButton Props
 *
 * Extends the shared BaseToggleProps with specific icon requirements
 */
interface ToggleIconButtonProps extends Omit<BaseToggleProps, "onToggle"> {
  onToggle: () => void; // Simplified from BaseToggleProps
  icon: React.ReactElement; // Icon to show when not hovered
  label?: string; // Made optional since ariaLabel is in BaseToggleProps
}

/**
 * A generic toggle button component that can be used for any toggle action
 *
 * @param isActive - Whether the button is in active state
 * @param onToggle - Callback when button is toggled
 * @param icon - Icon to show when not hovered
 * @param ariaLabel - Accessibility label for the button
 * @param size - Size variant from ComponentSize
 * @param isLoading - Whether the button is in loading state
 * @param isDisabled - Whether the button is disabled
 * @param label - Optional legacy label prop (use ariaLabel instead)
 */
const ToggleIconButton: React.FC<ToggleIconButtonProps> = ({
  isActive,
  onToggle,
  icon,
  ariaLabel,
  label, // Legacy support
  size = "sm",
  isLoading = false,
  isDisabled = false,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <IconButton
      aria-label={ariaLabel || label || "Toggle"}
      size={size}
      variant={!isActive && !isHovered ? "ghost" : "solid"}
      colorScheme={
        isHovered ? (isActive ? "red" : "orange") : isActive ? "blue" : "gray"
      }
      icon={isHovered ? isActive ? <TiMinus /> : <TiPlus /> : icon}
      fontSize={size}
      onClick={onToggle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      isLoading={isLoading}
      isDisabled={isDisabled}
    />
  );
};

export default ToggleIconButton;
