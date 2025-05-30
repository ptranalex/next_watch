import { Box, IconButton, useColorModeValue, useTheme } from "@chakra-ui/react";
import React, { useState } from "react";
import { TiMinus, TiPlus } from "react-icons/ti";

interface CardToggleIconButtonProps {
  isActive: boolean;
  onToggle: () => void;
  icon: React.ReactElement;
  label: string;
  size?: "sm" | "md" | "lg";
  isEnabled: boolean;
  isLoading?: boolean;
}

const CardToggleIconButton: React.FC<CardToggleIconButtonProps> = ({
  isActive,
  onToggle,
  icon,
  label,
  size = "md",
  isEnabled,
  isLoading = false,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const theme = useTheme();

  // Use semantic tokens and brand colors from theme
  const borderColor = useColorModeValue(
    isHovered
      ? isActive
        ? "feedback.error" // Use semantic error color for removal
        : "colors.primary" // Use brand primary for addition
      : isActive
      ? "colors.primary" // Active state uses brand primary
      : "text.tertiary", // Inactive state uses tertiary text color
    isHovered
      ? isActive
        ? "feedback.error"
        : "colors.primary"
      : isActive
      ? "colors.primary"
      : "text.tertiary"
  );

  // Define color scheme based on state using theme colors
  const getColorScheme = () => {
    if (isHovered) {
      return isActive ? "red" : "blue";
    }
    return isActive ? "blue" : "gray";
  };

  // Ensure minimum touch target size from theme
  const minTouchSize = theme.sizes.touch || "44px";

  return (
    <Box
      display="flex"
      alignItems="center"
      justifyContent="center"
      flexGrow={1}
      height="100%"
      width="100%"
      minHeight={minTouchSize} // Ensure touch-friendly minimum height
      borderRight={isActive ? "3px solid" : "none"}
      borderRightColor={borderColor}
      transition="all 0.2s ease-in-out" // Smooth transitions for better UX
    >
      <IconButton
        aria-label={label}
        height="100%"
        width="100%"
        minHeight={minTouchSize} // Touch-friendly minimum size
        minWidth={minTouchSize}
        flexGrow={1}
        borderRadius={0}
        variant={isHovered ? "solid" : "ghost"}
        colorScheme={getColorScheme()}
        icon={
          isEnabled ? (
            isHovered ? (
              isActive ? (
                <TiMinus />
              ) : (
                <TiPlus />
              )
            ) : (
              icon
            )
          ) : (
            <span style={{ visibility: "hidden" }}>{icon}</span>
          )
        }
        fontSize={size}
        isLoading={isLoading}
        onClick={onToggle}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        // Enhanced touch interactions for mobile
        onTouchStart={() => setIsHovered(true)}
        onTouchEnd={() => setIsHovered(false)}
        // Use semantic color for focus states
        _focus={{
          boxShadow: `0 0 0 3px ${useColorModeValue(
            theme.colors.brand.primary[300],
            theme.colors.brand.primary[600]
          )}66`, // 40% opacity
        }}
        // Improved active state for touch devices
        _active={{
          transform: "scale(0.95)",
          transition: "transform 0.1s ease-in-out",
        }}
        transition="all 0.2s ease-in-out"
      />
    </Box>
  );
};

export default CardToggleIconButton;
