"use client";

import { memo, useEffect } from "react";
import MovieGrid from "@/components/features/movies/grid/MovieGrid";
import MovieBrowseLayout from "@/components/ui/templates/MovieBrowseLayout";
import { useParams, useSearchParams, usePathname } from "next/navigation";
import useMovieFilterStore from "@/store/movieFilterStore";
import { Heading } from "@chakra-ui/react";
import { createLogger } from "@/utils/logging";

// Create a logger for this component
const logger = createLogger("TopMoviesPage");

// Make the page dynamic to avoid prerendering issues
export const dynamic = "force-dynamic";

// Memoize components
const MemoizedMovieGrid = memo(MovieGrid);

/**
 * TopMoviesByYearPage component - Shows top movies for a specific year
 *
 * Route: /top/[year]
 * Displays movies from the specified year sorted by IMDb rating
 * Special cases:
 * - top/current-year: Uses the current year and locks it
 * - top/all-time: Shows all years, no year filter is locked
 */
const TopMoviesByYearPage: React.FC = () => {
  const params = useParams<{ year: string }>();
  const yearParam = params?.year || "";
  const currentYear = new Date().getFullYear();
  const searchParams = useSearchParams();
  const pathname = usePathname();

  const { setFilter, lockFilters, unlockAllFilters } = useMovieFilterStore();

  // Set and lock the filters when the component mounts or year changes
  useEffect(() => {
    // Special cases handling
    if (yearParam === "current-year") {
      logger.info(`Setting top movies for current year: ${currentYear}`);

      unlockAllFilters();
      setFilter("year", currentYear);
      setFilter("sortOrder", "imdb_rating");
      setFilter("sortDesc", true);
      lockFilters(["year", "sortOrder"]);
    } else if (yearParam === "all-time") {
      logger.info("Setting top movies of all time");

      unlockAllFilters();
      // Clear year filter for all-time
      setFilter("year", undefined);
      setFilter("sortOrder", "imdb_rating");
      setFilter("sortDesc", true);
      lockFilters(["sortOrder"]); // Only lock sort order, not year
    } else {
      // Normal numeric year handling
      const year = parseInt(yearParam, 10);
      logger.info(`Setting top movies for year: ${year}`);

      unlockAllFilters();
      setFilter("year", year);
      setFilter("sortOrder", "imdb_rating");
      setFilter("sortDesc", true);
      lockFilters(["year", "sortOrder"]);
    }

    // Cleanup function: unlock filters when component unmounts or before re-running effect
    return () => {
      logger.debug(
        "🔓 Cleaning up: unlocking filters when leaving top/[year] page"
      );
      unlockAllFilters();
    };
  }, [
    yearParam,
    pathname,
    setFilter,
    lockFilters,
    unlockAllFilters,
    currentYear,
  ]);

  // Track search params for hydration
  useEffect(() => {
    // This forces React to include searchParams in hydration
    if (searchParams) {
      // Just accessing searchParams is enough to make React track it
      logger.debugOnce("Including searchParams in hydration");
    }
  }, [searchParams]);

  // Determine the title based on the route parameter
  let titleText = "";
  if (yearParam === "current-year") {
    titleText = `Top Movies of ${currentYear} (Current Year)`;
  } else if (yearParam === "all-time") {
    titleText = "Top Movies of All Time";
  } else {
    // Normal year handling
    const year = parseInt(yearParam, 10);
    titleText = `Top Movies from ${year || currentYear}`;
  }

  logger.debug(`Rendering page with title: ${titleText}`);

  const title = (
    <Heading as="h1" marginY={5}>
      {titleText}
    </Heading>
  );

  return (
    <MovieBrowseLayout title={title}>
      <MemoizedMovieGrid
        columns={{ base: 3, sm: 3, md: 4, lg: 6 }}
        source="movie_listing"
      />
    </MovieBrowseLayout>
  );
};

export default TopMoviesByYearPage;
