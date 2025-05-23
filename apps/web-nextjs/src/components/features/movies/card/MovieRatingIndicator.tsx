import { Box, Icon } from "@chakra-ui/react";
import { HiMiniStar } from "react-icons/hi2";

interface MovieRatingIndicatorProps {
  /**
   * The IMDB rating value to display
   * If undefined or null, no indicator is shown
   */
  rating?: number | null;

  /**
   * Custom positioning props - allows override of default positioning
   */
  position?: {
    top?: string | number;
    left?: string | number;
    bottom?: string | number;
    right?: string | number;
  };

  /**
   * Size of the star icon
   * @default 6
   */
  iconSize?: number | string;

  /**
   * Z-index for layering control
   * @default 0
   */
  zIndex?: number;
}

/**
 * MovieRatingIndicator - Displays a color-coded star indicator for movie ratings
 *
 * Color scheme based on IMDB rating:
 * - 8.0+: Primary dark color (excellent)
 * - 7.0+: Secondary dark color (very good)
 * - 6.0+: Tertiary dark color (good)
 * - Below 6.0: Hidden (not displayed)
 *
 * Positioned absolutely within its parent container by default (top-left corner).
 */
const MovieRatingIndicator: React.FC<MovieRatingIndicatorProps> = ({
  rating,
  position = { top: 0, left: 2 },
  iconSize = 6,
  zIndex = 0,
}) => {
  /**
   * Determines the color based on the rating value
   * Uses semantic color tokens from the theme
   */
  const getRatingColor = (value: number | null | undefined): string => {
    if (!value || typeof value !== "number") return "hidden";

    if (value >= 8.0) {
      return "colors.primary.darker"; // Excellent rating
    } else if (value >= 7.0) {
      return "colors.secondary.darker"; // Very good rating
    } else if (value >= 6.0) {
      return "text.primary"; // Good rating - use primary text color
    }

    return "hidden"; // Below 6.0 - don't show indicator
  };

  const color = getRatingColor(rating);

  // Don't render anything if rating should be hidden
  if (color === "hidden") {
    return null;
  }

  return (
    <Box
      position="absolute"
      zIndex={zIndex}
      marginBottom={2}
      marginTop={2}
      // Apply positioning with defaults and allow overrides
      top={position.top}
      left={position.left}
      bottom={position.bottom}
      right={position.right}
      // Ensure proper layering and accessibility
      role="img"
      aria-label={`Rating: ${rating} out of 10 stars`}
    >
      <Icon
        as={HiMiniStar}
        boxSize={iconSize}
        color={color}
        // Add subtle drop shadow for better visibility on various backgrounds
        filter="drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3))"
        transition="all 0.2s ease-in-out"
        // Hover effect for better interactivity feedback
        _hover={{
          transform: "scale(1.1)",
          filter: "drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4))",
        }}
      />
    </Box>
  );
};

export default MovieRatingIndicator;
