import { Movie } from "@/domain/entities";
import userInteractionAPI from "@/services/api/user/user-interaction-api";
import {
  Box,
  IconButton,
  useColorModeValue,
  useToast,
  useTheme,
} from "@chakra-ui/react";
import React, { useEffect, useState } from "react";
import { TiMinus, TiPlus } from "react-icons/ti";

interface ToggleIconButtonProps {
  movie: Movie;
  attribute: "watched" | "liked" | "in_watchlist"; // The attribute to toggle
  endpoint: "watched" | "liked" | "towatch"; // The API endpoint to use
  onToggle: (value: boolean) => void;
  icon: React.ReactElement; // Icon to show when the attribute is true
  label: string; // Aria label for the button
  size?: "sm" | "md" | "lg";
  isEnabled: boolean; // Prop to indicate blur effect
}

const CardToggleIconButton: React.FC<ToggleIconButtonProps> = ({
  movie,
  attribute,
  endpoint,
  onToggle,
  icon,
  label,
  size = "md", // Changed default to md for better touch targets
  isEnabled,
}) => {
  const [isActive, setIsActive] = useState(movie[attribute]);
  const [isHovered, setIsHovered] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();
  const theme = useTheme();

  const toggleAttribute = async (isActive: boolean) => {
    // Call the onToggle callback to update UI state immediately for responsive UI
    onToggle(isActive);
    setIsLoading(true);

    // Ensure movie.id is a number
    if (typeof movie.id !== "number") {
      console.error("Movie ID is not a number:", movie.id);
      toast({
        title: "Action failed",
        description: `Invalid movie ID for ${movie.title}. Please try again.`,
        status: "error",
        duration: 5000,
        isClosable: true,
        position: "bottom-right",
      });
      setIsLoading(false);
      return;
    }

    try {
      // Call the appropriate API method based on the endpoint
      if (endpoint === "watched") {
        await userInteractionAPI.toggleWatched(movie.id);
      } else if (endpoint === "liked") {
        await userInteractionAPI.toggleLiked(movie.id);
      } else if (endpoint === "towatch") {
        await userInteractionAPI.toggleWatchlist(movie.id);
      }

      // Show success toast
      toast({
        title: `${isActive ? "Added to" : "Removed from"} ${endpoint}`,
        description: `${movie.title} was ${
          isActive ? "added to" : "removed from"
        } your ${endpoint} list.`,
        status: "success",
        duration: 3000,
        isClosable: true,
        position: "bottom-right",
      });
    } catch (error) {
      // Revert the UI state if the API call fails
      onToggle(!isActive);

      // Show error toast
      toast({
        title: "Action failed",
        description: `Could not update ${endpoint} status for ${movie.title}. Please try again.`,
        status: "error",
        duration: 5000,
        isClosable: true,
        position: "bottom-right",
      });

      console.error(`Error toggling ${endpoint} for movie ${movie.id}:`, error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    setIsActive(movie[attribute]);
  }, [movie, attribute]);

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
        onClick={() => toggleAttribute(!isActive)}
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
