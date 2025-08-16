"use client";

import { useEffect } from "react";
import { Heading } from "@chakra-ui/react";
import MovieBrowseLayout from "@/components/ui/layout/MovieBrowseLayout";
import { createLogger } from "@/utils/logging";
import { useResponsive } from "@/providers/ResponsiveContext";
import { useHomePage } from "@/services/hooks/pages";
import MovieGrid from "@/components/features/movies/grid/MovieGrid";

// Create logger for this component
const logger = createLogger("HomePage");

/**
 * HomePage component - Entry point for the application's main page
 *
 * This is a feature-level component that contains all the business logic
 * for displaying the home page movies, handling responsive behavior,
 * device-specific layouts, and managing pagination state.
 *
 * Uses the shared MovieBrowseLayout with true mobile-first approach
 * Hydration-aware to prevent layout shifts
 */
const HomePage: React.FC = () => {
  // Log component initialization
  logger.debug("HomePage feature component initializing");

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

  // Use the home page hook to fetch movies
  const {
    movies,
    totalMovies,
    fetchedMoviesCount,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    fetchNextPage,
    error,
  } = useHomePage({});

  // Log when movies data changes
  useEffect(() => {
    if (movies && movies.length > 0) {
      logger.info(`Home page data loaded: ${movies.length} movies`);
    }
  }, [movies]);

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
      <MovieGrid
        movies={movies}
        totalMovies={totalMovies}
        fetchedMoviesCount={fetchedMoviesCount}
        isLoading={isLoading}
        isFetchingNextPage={isFetchingNextPage}
        hasNextPage={hasNextPage}
        onLoadMore={fetchNextPage}
        error={error as Error | null}
        columns={{
          base: 2, // 2 columns on small phones (iPhone SE, iPhone 13 mini)
          sm: 3, // 3 columns on larger phones (iPhone 14+, iPhone 14 Pro Max)
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
