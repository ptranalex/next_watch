"use client";

import ScrollToTopButton from "@/components/commons/ScrollToTopButton";
import MovieCard from "@/components/movieCard/MovieCard";
import MovieCardContainer from "@/components/movieCard/MovieCardContainer";
import MovieCardSkeleton from "@/components/movieCard/MovieCardSkeleton";
import { Movie } from "@/domain/entities";
import { useMovies } from "@/hooks";
import useMovieFilterStore from "@/store/movieFilterStore";
import { Box, SimpleGrid, Text, useBreakpointValue } from "@chakra-ui/react";
import { usePathname } from "next/navigation";
import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("MovieGrid");

type ColumnBreakpoints =
  | {
      [key in "base" | "sm" | "md" | "lg" | "xl"]?: number;
    }
  | number
  | number[];

interface MovieGridProps {
  columns: ColumnBreakpoints;
  source:
    | "movie_listing"
    | "more_like_this"
    | "by_actor"
    | "watchlist"
    | "favorites"
    | "watched";
  movie_id?: number;
  actor_id?: number;
  genre_id?: number;
}

// First, let's change the MovieSkeletonGrid component to support inline rendering
const MovieSkeletonGrid = React.memo(
  ({
    columns,
    count,
    inline = false,
  }: {
    columns: ColumnBreakpoints;
    count: number;
    inline?: boolean;
  }) => {
    const skeletonsArray = Array.from({ length: count }, (_, i) => i + 1);

    if (inline) {
      // Just return the skeleton items without wrapping SimpleGrid
      return (
        <>
          {skeletonsArray.map((key) => (
            <MovieCardContainer key={`skeleton-${key}`}>
              <MovieCardSkeleton />
            </MovieCardContainer>
          ))}
        </>
      );
    }

    // Original behavior with wrapping SimpleGrid
    return (
      <SimpleGrid columns={columns} spacing={3} padding={1}>
        {skeletonsArray.map((key) => (
          <MovieCardContainer key={`skeleton-${key}`}>
            <MovieCardSkeleton />
          </MovieCardContainer>
        ))}
      </SimpleGrid>
    );
  }
);
MovieSkeletonGrid.displayName = "MovieSkeletonGrid";

// Main component - memoized to prevent unnecessary re-renders from parent
const MovieGrid = React.memo(
  ({ columns, source, movie_id, actor_id, genre_id }: MovieGridProps) => {
    const [loadingNextPage, setLoadingNextPage] = useState(false);
    const [screenItemCapacity, setScreenItemCapacity] = useState(0);
    const [initialLoadComplete, setInitialLoadComplete] = useState(false);
    // Start as true for consistent server/client rendering, manage in useEffect
    const [initialDataLoaded, setInitialDataLoaded] = useState(true);
    const scrollContainerRef = useRef<HTMLDivElement>(null);
    const pathname = usePathname();

    // Get store filters to watch for changes
    const { filters } = useMovieFilterStore();

    // Log component initialization with source and ID details
    useEffect(() => {
      logger.info(`MovieGrid initialized - source: ${source}`, {
        movie_id,
        actor_id,
        genre_id,
        filters,
      });

      return () => {
        logger.debug("MovieGrid unmounting");
      };
    }, [source, movie_id, actor_id, genre_id, filters]);

    // Server-side compatible hydration - use useEffect for client-only behavior
    useEffect(() => {
      // Only on client, we can afford to show loading temporarily
      if (typeof window !== "undefined") {
        setInitialDataLoaded(false);
        const timer = setTimeout(() => {
          setInitialDataLoaded(true);
          logger.debug("Initial data loading state reset after hydration");
        }, 50);
        return () => clearTimeout(timer);
      }
    }, []);

    // Check URL path for year parameter in the /top/[year] pattern
    const topYearPattern = /^\/top\/(\d{4})$/;
    const yearMatch = pathname ? pathname.match(topYearPattern) : null;
    const yearFromPath = yearMatch ? parseInt(yearMatch[1], 10) : null;

    if (yearFromPath) {
      logger.debug(`Year from path detected: ${yearFromPath}`);
    }

    // Memoize these values to prevent recalculation on every render
    const safeIds = useMemo(
      () => ({
        movieId:
          typeof movie_id === "number" && movie_id > 0 ? movie_id : undefined,
        actorId:
          typeof actor_id === "number" && actor_id > 0 ? actor_id : undefined,
        genreId:
          typeof genre_id === "number" && genre_id > 0 ? genre_id : undefined,
      }),
      [movie_id, actor_id, genre_id]
    );

    // Reset initialLoadComplete when source/ids/filters change
    useEffect(() => {
      // Only run on the client side
      if (typeof window === "undefined") return;

      // Reset both states when filters or source changes
      setInitialLoadComplete(false);
      // Also reset initial data loaded to trigger fresh skeleton loading state
      setInitialDataLoaded(false);

      logger.info("Resetting grid for new filter/source", {
        source,
        movieId: safeIds.movieId,
        actorId: safeIds.actorId,
        genreId: safeIds.genreId,
        filters: {
          imdb_rating: filters.imdb_rating,
          rotten_tomatoes_rating: filters.rotten_tomatoes_rating,
          metacritic_rating: filters.metacritic_rating,
          year: filters.year,
          sortOrder: filters.sortOrder,
        },
      });

      // Re-enable initial data loaded after a short delay
      const timer = setTimeout(() => {
        setInitialDataLoaded(true);
      }, 50);

      return () => clearTimeout(timer);
    }, [
      // Reset when filters change too
      filters.imdb_rating,
      filters.rotten_tomatoes_rating,
      filters.metacritic_rating,
      filters.year,
      filters.sortOrder,
      // Reset when source or IDs change
      source,
      safeIds.movieId,
      safeIds.actorId,
      safeIds.genreId,
    ]);

    const { data, isLoading, fetchNextPage, hasNextPage, updateMovie, error } =
      useMovies({
        source,
        movie_id: safeIds.movieId,
        actor_id: safeIds.actorId,
        genre_id: safeIds.genreId,
      });

    // Log when data changes or errors
    useEffect(() => {
      if (error) {
        logger.error("Error fetching movies:", error);
      } else if (data?.pages) {
        const movieCount = data.pages.reduce(
          (count, page) => count + (page.movies?.length || 0),
          0
        );
        logger.info(
          `Movies data loaded: ${movieCount} movies across ${data.pages.length} pages`
        );
      }
    }, [data?.pages, error]);

    const breakpointColumns = useBreakpointValue(
      columns as Record<string, number>
    );

    // Log when breakpoints change
    useEffect(() => {
      logger.debug(`Grid columns updated: ${breakpointColumns}`);
    }, [breakpointColumns]);

    // Memoize the skeleton counts
    const skeletonCounts = useMemo(() => {
      const numCols =
        typeof breakpointColumns === "number" ? breakpointColumns : 4;

      // Fixed constants instead of window-dependent calculations for server/client consistency
      // These values are used only for initial rendering before hydration
      const initialRows = 6; // Use a fixed number of rows for initial server render

      return {
        // Fixed number for server rendering to prevent hydration mismatch
        initial: numCols * initialRows,
        // Next page loads should be at least one row
        next: Math.max(numCols, 2 * numCols - (numCols % 2)),
      };
    }, [breakpointColumns]);

    // Calculate screen capacity on mount and resize - memoized calculation
    useEffect(() => {
      // Skip on server-side
      if (typeof window === "undefined") return;

      const calculateCapacity = () => {
        // Get viewport height (subtract some space for headers)
        const viewportHeight = window.innerHeight - 200;
        // Estimate movie card height (adjust based on your specific card)
        const estimatedItemHeight = 350;
        // Get number of columns
        const cols =
          typeof breakpointColumns === "number" ? breakpointColumns : 4;
        // Calculate how many rows would fit in viewport
        const rows = Math.ceil(viewportHeight / estimatedItemHeight);
        // Total items capacity = rows * columns
        const capacity = rows * cols;

        logger.debug(
          `Screen capacity calculated: ${capacity} items (${rows} rows × ${cols} columns)`
        );
        setScreenItemCapacity(capacity);
      };

      // Calculate initially
      calculateCapacity();

      // Debounce resize calculation for better performance
      let resizeTimer: NodeJS.Timeout;
      const handleResize = () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(calculateCapacity, 100);
      };

      // Recalculate on resize
      window.addEventListener("resize", handleResize);
      return () => {
        window.removeEventListener("resize", handleResize);
        clearTimeout(resizeTimer);
      };
    }, [breakpointColumns]);

    // Track number of pages loaded
    const [pagesLoaded, setPagesLoaded] = useState(0);

    // Update pagesLoaded when data changes
    useEffect(() => {
      if (data?.pages) {
        setPagesLoaded(data.pages.length);
      }
    }, [data?.pages?.length]);

    // Handle fetchNextPage
    const handleFetchNextPage = useCallback(async () => {
      if (!fetchNextPage || loadingNextPage) return;

      logger.info("Fetching next page of movies");
      setLoadingNextPage(true);
      await fetchNextPage();
      setLoadingNextPage(false);
    }, [fetchNextPage, loadingNextPage]);

    // Calculate fetchedMoviesCount when data is available
    const fetchedMoviesCount = useMemo(
      () =>
        data?.pages?.reduce(
          (total, page) =>
            total + (Array.isArray(page.movies) ? page.movies.length : 0),
          0
        ) || 0,
      [data?.pages]
    );

    // Memoize movie update handler
    const handleMovieUpdate = useCallback(
      (movie: Movie) => {
        if (typeof updateMovie === "function") {
          logger.debug(`Movie updated: ${movie.id} - ${movie.title}`);
          updateMovie(movie);
        }
      },
      [updateMovie]
    );

    // Prefetch logic to ensure screen has enough content
    useEffect(() => {
      // Skip prefetching for watchlist and favorites since we load everything at once
      if (source === "watchlist" || source === "favorites") return;

      // Only run if we have initial data, have more to load, aren't already loading,
      // haven't completed initial loading, and know screen capacity
      if (
        data &&
        hasNextPage &&
        !loadingNextPage &&
        !initialLoadComplete &&
        screenItemCapacity > 0 &&
        !isLoading
      ) {
        // Always load at least 2 pages for initial data (minimum standard)
        const needsMorePages = pagesLoaded < 2;

        // Check if content doesn't fill screen based on item count
        const needsMoreContent = fetchedMoviesCount < screenItemCapacity * 1.5;

        // Fetch more if either condition is met
        if (needsMorePages || needsMoreContent) {
          logger.info("Prefetching more content:", {
            pagesLoaded,
            fetchedMoviesCount,
            screenItemCapacity,
            needsMorePages,
            needsMoreContent,
          });

          handleFetchNextPage().then(() => {
            // Only mark as complete if we have enough pages AND content
            if (
              pagesLoaded >= 2 &&
              fetchedMoviesCount >= screenItemCapacity * 1.5
            ) {
              logger.debug("Setting initial load complete");
              setInitialLoadComplete(true);
            }
          });
        } else {
          // We already have enough content
          logger.debug("Already have enough content");
          setInitialLoadComplete(true);
        }
      }
    }, [
      data,
      fetchedMoviesCount,
      screenItemCapacity,
      hasNextPage,
      isLoading,
      loadingNextPage,
      initialLoadComplete,
      handleFetchNextPage,
      source,
      pagesLoaded,
    ]);

    // After the existing useEffect for prefetching content, add this new effect
    // Check if content fills the screen after rendering and fetch more if needed
    useEffect(() => {
      // Skip for sources that don't use infinite loading
      if (source === "watchlist" || source === "favorites") return;

      // Skip if we're already loading or there's no more data
      if (loadingNextPage || !hasNextPage || isLoading) return;

      // Skip if we haven't received initial data yet
      if (!data?.pages || fetchedMoviesCount === 0) return;

      // Only run this check once initial rendering is settled
      const checkContentHeight = () => {
        if (!scrollContainerRef.current) return;

        const container = scrollContainerRef.current;
        const contentHeight = container.scrollHeight;
        const viewportHeight = window.innerHeight;
        const containerTop = container.getBoundingClientRect().top;
        const visibleContainerHeight = viewportHeight - containerTop;

        // If content doesn't fill the container, fetch more data
        if (contentHeight < visibleContainerHeight && hasNextPage) {
          logger.info("Content height insufficient, fetching more data:", {
            contentHeight,
            visibleContainerHeight,
            fetchedMoviesCount,
          });
          handleFetchNextPage();
        }
      };

      // Run after a short delay to ensure rendering is complete
      const timer = setTimeout(checkContentHeight, 300);

      return () => clearTimeout(timer);
    }, [
      fetchedMoviesCount,
      hasNextPage,
      loadingNextPage,
      isLoading,
      handleFetchNextPage,
      data?.pages,
      source,
    ]);

    // Memoize movie list to prevent unnecessary re-renders
    const movieList = useMemo(() => {
      if (!data || !data.pages) return [];

      return data.pages.flatMap((page, pageIndex) =>
        Array.isArray(page.movies)
          ? page.movies
              .filter(
                (movie: Movie | null) =>
                  movie && typeof movie === "object" && movie.id
              )
              .map((movie: Movie) => (
                <MovieCardContainer key={`${pageIndex}-${movie.id}`}>
                  <MovieCard movie={movie} onMovieUpdate={handleMovieUpdate} />
                </MovieCardContainer>
              ))
          : []
      );
    }, [data?.pages, handleMovieUpdate]);

    // Handle error states
    if (error) {
      logger.error("Error fetching movies:", error);
      return <Text>Error loading movies. Please try again later.</Text>;
    }

    // Handle loading state
    if (isLoading || !initialDataLoaded) {
      // Use a fixed skeleton count for consistent server/client rendering
      const fixedSkeletonCount =
        typeof breakpointColumns === "number"
          ? breakpointColumns * 6 // 6 rows for consistency
          : 24; // Default to 24 items (6 rows of 4 columns)

      logger.debug(`Showing loading skeleton with ${fixedSkeletonCount} items`);
      return <MovieSkeletonGrid columns={columns} count={fixedSkeletonCount} />;
    }

    // Handle empty states
    if (
      !data ||
      !data.pages ||
      data.pages.length === 0 ||
      fetchedMoviesCount === 0
    ) {
      logger.info("No movies found for current filters");
      return <Text>No movies found</Text>;
    }

    logger.debug(
      `Rendering ${fetchedMoviesCount} movies in ${data.pages.length} pages`
    );

    return (
      <Box ref={scrollContainerRef}>
        {source === "watchlist" || source === "favorites" ? (
          // For watchlist and favorites, use a simple grid without infinite scrolling
          <SimpleGrid columns={columns} spacing={3} padding={1}>
            {movieList}
            {fetchedMoviesCount === 0 && (
              <Text textAlign="center" py={4} gridColumn="1 / -1">
                {source === "favorites"
                  ? "You haven't liked any movies yet"
                  : "Your watchlist is empty"}
              </Text>
            )}
          </SimpleGrid>
        ) : (
          // For other sources including watched, use infinite scrolling
          <InfiniteScroll
            dataLength={fetchedMoviesCount}
            next={handleFetchNextPage}
            hasMore={!!hasNextPage}
            loader={null}
            scrollThreshold={0.5}
            endMessage={
              <Text textAlign="center" py={4}>
                {fetchedMoviesCount > 0
                  ? "No more movies to load"
                  : source === "watched"
                  ? "You haven't watched any movies yet"
                  : "No movies found"}
              </Text>
            }
          >
            <SimpleGrid columns={columns} spacing={3} padding={1}>
              {movieList}
              {loadingNextPage && hasNextPage && (
                <MovieSkeletonGrid
                  columns={columns}
                  count={skeletonCounts.next}
                  inline={true}
                />
              )}
            </SimpleGrid>
          </InfiniteScroll>
        )}
        <ScrollToTopButton />
      </Box>
    );
  }
);

MovieGrid.displayName = "MovieGrid";

export default MovieGrid;
