import { IconButton } from "@chakra-ui/react";
import React, { useState } from "react";
import { TiMinus, TiPlus } from "react-icons/ti";

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

  // Get appropriate colors based on state
  const getButtonProps = () => {
    if (isHovered) {
      if (isActive) {
        // Hover on active - remove action
        return {
          bg: "feedback.error",
          color: "text.inverse",
          variant: "solid",
        };
      } else {
        // Hover on inactive - add action
        return {
          bg: "colors.secondary",
          color: "text.inverse",
          variant: "solid",
        };
      }
    } else {
      if (isActive) {
        // Active state
        return {
          bg: "colors.primary",
          color: "text.inverse",
          variant: "solid",
        };
      } else {
        // Inactive state
        return {
          bg: "transparent",
          color: "text.secondary",
          variant: "ghost",
        };
      }
    }
  };

  const buttonProps = getButtonProps();

  return (
    <IconButton
      aria-label={label}
      size={size}
      variant={buttonProps.variant}
      bg={buttonProps.bg}
      color={buttonProps.color}
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
