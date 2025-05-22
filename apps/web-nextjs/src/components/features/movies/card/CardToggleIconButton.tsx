import { Movie } from "@/domain/entities";
import userInteractionAPI from "@/services/api/user/user-interaction-api";
import { Box, IconButton, useColorModeValue, useToast } from "@chakra-ui/react";
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
  size = "sm",
  isEnabled,
}) => {
  const [isActive, setIsActive] = useState(movie[attribute]);
  const [isHovered, setIsHovered] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();

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

  const borderColor = useColorModeValue(
    isHovered
      ? isActive
        ? "feedback.error"
        : "colors.primary"
      : isActive
      ? "colors.primary"
      : "bg.tertiary",
    isHovered
      ? isActive
        ? "feedback.error"
        : "colors.primary"
      : isActive
      ? "colors.primary"
      : "bg.secondary"
  );

  // Get button styles based on state
  const getButtonStyles = () => {
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

  const buttonStyles = getButtonStyles();

  return (
    <Box
      display="flex"
      alignItems="center"
      justifyContent="center"
      flexGrow={1}
      height="100%"
      width="100%"
      borderRight={isActive ? "3px solid" : "none"}
      borderRightColor={borderColor}
    >
      <IconButton
        aria-label={label}
        height="100%"
        width="100%"
        flexGrow={1}
        borderRadius={0}
        variant={buttonStyles.variant}
        bg={buttonStyles.bg}
        color={buttonStyles.color}
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
      />
    </Box>
  );
};

export default CardToggleIconButton;
