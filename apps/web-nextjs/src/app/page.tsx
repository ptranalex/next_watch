"use client";

import { memo, useEffect } from "react";
import { Heading } from "@chakra-ui/react";
import MovieGrid from "@/components/features/movies/grid/MovieGrid";
import MovieBrowseLayout from "@/components/ui/templates/MovieBrowseLayout";
import { createLogger } from "@/utils/logging";
import { useResponsive } from "@/providers/ResponsiveContext";

// Create logger for this component
const logger = createLogger("HomePage");

// Make the page dynamic to avoid prerendering issues
export const dynamic = "force-dynamic";

// Memoize components
const MemoizedMovieGrid = memo(MovieGrid);

/**
 * HomePage component - Entry point for the application's main page
 *
 * Uses the shared MovieBrowseLayout with true mobile-first approach
 * Hydration-aware to prevent layout shifts
 */
const HomePage: React.FC = () => {
  // Use our centralized responsive context instead of direct media queries
  const { isMobile, isTablet, isDesktop, hasTouchScreen, isHydrated } =
    useResponsive();

  // Log component mount with device type
  useEffect(() => {
    if (isHydrated) {
      logger.info(
        `HomePage mounted - displaying all movies (${
          isMobile ? "mobile" : isTablet ? "tablet" : "desktop"
        } view)`
      );

      // Log more detailed device information
      logger.debug(
        `Device details: mobile=${isMobile}, tablet=${isTablet}, desktop=${isDesktop}, touch=${hasTouchScreen}`
      );
    }
  }, [isMobile, isTablet, isDesktop, hasTouchScreen, isHydrated]);

  // Responsive title with different styling based on device type
  const title = (
    <Heading
      as="h1"
      fontSize={{ base: "xl", sm: "2xl", md: "3xl" }}
      marginY={{ base: 3, md: 5 }}
      textAlign={{ base: "center", md: "left" }}
    >
      All Movies
    </Heading>
  );

  // Only log rendering after hydration
  if (isHydrated) {
    logger.debug(
      `Rendering HomePage with MovieGrid (${
        isMobile ? "mobile" : isTablet ? "tablet" : "desktop"
      } view)`
    );
  }

  return (
    <MovieBrowseLayout title={title}>
      <MemoizedMovieGrid
        // Fully responsive grid columns based on exact device type
        columns={{
          base: 2, // 2 columns on very small mobile screens
          sm: isMobile ? 3 : 4, // 3 columns on mobile, 4 on small tablet
          md: isTablet ? 4 : 5, // 4 columns on tablet, 5 on small desktop
          lg: 6, // 6 columns on large screens
          xl: 8, // 8 columns on extra large screens
        }}
        source="movie_listing"
      />
    </MovieBrowseLayout>
  );
};

export default HomePage;
