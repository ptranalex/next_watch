"use client";

import ScrollToTopButton from "@/components/ui/molecules/ScrollToTopButton";
import {
  MovieCard,
  MovieCardContainer,
  MovieCardSkeleton,
} from "@/components/features/movies/card";
import { Movie } from "@/domain/entities";
import { Box, SimpleGrid, Text, useBreakpointValue } from "@chakra-ui/react";
import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import InfiniteScroll from "react-infinite-scroll-component";
import { createLogger } from "@/utils/logging";
import { useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/services/hooks";

// Create logger for this component
const logger = createLogger("MovieGrid");

// Column breakpoints type
type ColumnBreakpoints =
  | {
      [key in "base" | "sm" | "md" | "lg" | "xl"]?: number;
    }
  | number
  | number[];

interface MovieGridProps {
  // Data props
  movies: Movie[];
  totalMovies: number;
  fetchedMoviesCount: number;

  // Loading states
  isLoading: boolean;
  isFetchingNextPage: boolean;

  // Pagination
  hasNextPage?: boolean;
  onLoadMore?: () => void;

  // Error handling
  error?: Error | null;

  // UI props
  columns: ColumnBreakpoints;
  source?: string; // For logging purposes

  // Empty state message
  emptyMessage?: string;
}

// Memoized skeleton grid component
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

/**
 * MovieGrid component - Pure UI component for displaying movies
 *
 * This component receives movies as props and handles only the rendering concerns.
 * Data fetching is handled by the parent component using appropriate hooks.
 */
const MovieGrid = React.memo<MovieGridProps>(
  ({
    movies,
    totalMovies,
    fetchedMoviesCount,
    isLoading,
    isFetchingNextPage,
    hasNextPage,
    onLoadMore,
    error,
    columns,
    source = "unknown",
    emptyMessage = "No movies found",
  }) => {
    const [loadingNextPage, setLoadingNextPage] = useState(false);
    const scrollContainerRef = useRef<HTMLDivElement>(null);
    const queryClient = useQueryClient();
    const { isAuthenticated } = useAuth();

    // Get responsive column count
    const breakpointColumns = useBreakpointValue(
      typeof columns === "object" && !Array.isArray(columns)
        ? columns
        : { base: 4 }
    );

    // Log component initialization
    useEffect(() => {
      logger.info(`MovieGrid initialized for source: ${source}`, {
        moviesCount: movies.length,
        totalMovies,
        fetchedMoviesCount,
      });
    }, [source, movies.length, totalMovies, fetchedMoviesCount]);

    // Handle movie updates (for user interactions like like/watchlist)
    const handleMovieUpdate = useCallback(
      async (updatedMovie: Movie) => {
        if (!isAuthenticated) {
          logger.warn("User not authenticated, cannot update movie");
          return;
        }

        try {
          logger.debug(`Updating movie ${updatedMovie.id}:`, updatedMovie);

          // The movie update logic will be handled by the MovieCard component
          // This is just for invalidating queries after updates
          queryClient.invalidateQueries({ queryKey: ["bff-movies"] });
          queryClient.invalidateQueries({
            queryKey: ["movieInteraction", updatedMovie.id],
          });

          logger.info(`Movie ${updatedMovie.id} updated successfully`);
        } catch (error) {
          logger.error(`Failed to update movie ${updatedMovie.id}:`, error);
          throw error;
        }
      },
      [isAuthenticated, queryClient]
    );

    // Handle infinite scroll loading
    const handleFetchNextPage = useCallback(async () => {
      if (
        !hasNextPage ||
        loadingNextPage ||
        isFetchingNextPage ||
        !onLoadMore
      ) {
        return;
      }

      logger.debug("Fetching next page of movies");
      setLoadingNextPage(true);

      try {
        await onLoadMore();
      } catch (error) {
        logger.error("Error fetching next page:", error);
      } finally {
        setLoadingNextPage(false);
      }
    }, [hasNextPage, loadingNextPage, isFetchingNextPage, onLoadMore]);

    // Calculate skeleton counts
    const skeletonCounts = useMemo(() => {
      const baseCount =
        typeof breakpointColumns === "number" ? breakpointColumns : 4;
      return {
        initial: baseCount * 6, // 6 rows for initial load
        next: baseCount * 2, // 2 rows for next page
      };
    }, [breakpointColumns]);

    // Memoize movie list to prevent unnecessary re-renders
    const movieList = useMemo(() => {
      return movies
        .filter(
          (movie) =>
            (typeof movie.id === "string" || typeof movie.id === "number") &&
            !!movie.id
        )
        .map((movie) => (
          <MovieCardContainer key={String(movie.id)}>
            <MovieCard movie={movie} onMovieUpdate={handleMovieUpdate} />
          </MovieCardContainer>
        ));
    }, [movies, handleMovieUpdate]);

    // Auto-fetch more content if viewport is not filled
    useEffect(() => {
      if (isLoading || !hasNextPage || fetchedMoviesCount === 0) return;

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

      const timer = setTimeout(checkContentHeight, 300);
      return () => clearTimeout(timer);
    }, [
      fetchedMoviesCount,
      hasNextPage,
      loadingNextPage,
      isLoading,
      handleFetchNextPage,
    ]);

    // Handle error states
    if (error) {
      logger.error("Error in MovieGrid:", error);
      return (
        <Text color="feedback.error">
          Error loading movies. Please try again later.
        </Text>
      );
    }

    // Handle loading state
    if (isLoading) {
      logger.debug(
        `Showing loading skeleton with ${skeletonCounts.initial} items`
      );
      return (
        <MovieSkeletonGrid columns={columns} count={skeletonCounts.initial} />
      );
    }

    // Handle empty states
    if (movies.length === 0) {
      logger.info("No movies to display");
      return <Text color="text.tertiary">{emptyMessage}</Text>;
    }

    logger.debug(`Rendering ${movies.length} movies from ${source}`);

    return (
      <Box ref={scrollContainerRef}>
        <InfiniteScroll
          dataLength={fetchedMoviesCount}
          next={handleFetchNextPage}
          hasMore={!!hasNextPage}
          loader={null}
          scrollThreshold={0.5}
          style={{
            paddingTop: 2,
          }}
          endMessage={
            <Text textAlign="center" py={4} color="text.tertiary">
              {fetchedMoviesCount > 0 ? "No more movies to load" : emptyMessage}
            </Text>
          }
        >
          <SimpleGrid columns={columns} spacing={3} padding={1}>
            {movieList}
            {(loadingNextPage || isFetchingNextPage) && hasNextPage && (
              <MovieSkeletonGrid
                columns={columns}
                count={skeletonCounts.next}
                inline={true}
              />
            )}
          </SimpleGrid>
        </InfiniteScroll>
        <ScrollToTopButton />
      </Box>
    );
  }
);

MovieGrid.displayName = "MovieGrid";

export default MovieGrid;
