import { IconButton, useColorModeValue, useTheme } from "@chakra-ui/react";
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
 *
 * Features:
 * - Theme-integrated colors using semantic tokens
 * - Mobile-first touch-friendly design
 * - Smooth animations and transitions
 * - Enhanced accessibility with proper focus states
 */
const ToggleIconButton: React.FC<ToggleIconButtonProps> = ({
  isActive,
  onToggle,
  icon,
  label,
  size = "md", // Changed default to md for better touch targets
  isLoading = false,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const theme = useTheme();

  // Use semantic tokens and brand colors from theme
  const getColorScheme = () => {
    if (isHovered) {
      return isActive ? "red" : "blue"; // Red for removal, blue for addition
    }
    return isActive ? "blue" : "gray"; // Blue for active state, gray for inactive
  };

  // Get button variant based on state
  const getVariant = () => {
    if (!isActive && !isHovered) {
      return "ghost"; // Subtle when inactive and not hovered
    }
    return "solid"; // Prominent when active or hovered
  };

  // Ensure minimum touch target size from theme
  const minTouchSize = theme.sizes.touch || "44px";

  // Enhanced focus ring using brand colors
  const focusRing = useColorModeValue(
    `0 0 0 3px ${theme.colors.brand.primary[300]}66`, // 40% opacity
    `0 0 0 3px ${theme.colors.brand.primary[600]}66`
  );

  return (
    <IconButton
      aria-label={label}
      size={size}
      minHeight={minTouchSize} // Ensure touch-friendly minimum size
      minWidth={minTouchSize}
      variant={getVariant()}
      colorScheme={getColorScheme()}
      icon={isHovered ? isActive ? <TiMinus /> : <TiPlus /> : icon}
      fontSize={size}
      onClick={onToggle}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      // Enhanced touch interactions for mobile
      onTouchStart={() => setIsHovered(true)}
      onTouchEnd={() => setIsHovered(false)}
      isLoading={isLoading}
      // Enhanced focus state using theme colors
      _focus={{
        boxShadow: focusRing,
        outline: "none",
      }}
      // Improved active state for touch devices
      _active={{
        transform: "scale(0.95)",
        transition: "transform 0.1s ease-in-out",
      }}
      // Smooth transitions for better UX
      transition="all 0.2s ease-in-out"
      // Enhanced hover state
      _hover={{
        transform: "scale(1.05)",
      }}
      // Ensure proper disabled state styling
      _disabled={{
        opacity: 0.6,
        cursor: "not-allowed",
        transform: "none",
      }}
    />
  );
};

export default ToggleIconButton;
