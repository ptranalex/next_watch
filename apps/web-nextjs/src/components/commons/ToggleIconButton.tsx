import { IconButton } from "@chakra-ui/react";
import React, { useState } from "react";
import { TiPlus } from "react-icons/ti";
import { TiMinus } from "react-icons/ti";

interface ToggleIconButtonProps {
  isActive: boolean;
  onToggle: () => void;
  icon: React.ReactElement; // Icon to show when not hovered
  label: string; // Aria label for the button
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

/**
 * A generic toggle button component that can be used for any toggle action
 * It doesn't have any domain-specific logic, making it reusable across the app
 */
const ToggleIconButton: React.FC<ToggleIconButtonProps> = ({
  isActive,
  onToggle,
  icon,
  label,
  size = "sm",
  isLoading = false,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <IconButton
      aria-label={label}
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
    />
  );
};

export default ToggleIconButton;
