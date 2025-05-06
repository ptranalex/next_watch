"use client";

import { Box, SimpleGrid, Text, useBreakpointValue } from "@chakra-ui/react";
import React, {
  useState,
  useEffect,
  useRef,
  useMemo,
  useCallback,
} from "react";
import { useSearchParams } from "next/navigation";
import InfiniteScroll from "react-infinite-scroll-component";
import { useMovies } from "@/hooks";
import MovieCard from "@/components/movieCard/MovieCard";
import MovieCardContainer from "@/components/movieCard/MovieCardContainer";
import MovieCardSkeleton from "@/components/movieCard/MovieCardSkeleton";
import ScrollToTopButton from "@/components/commons/ScrollToTopButton";
import { Movie } from "@/domain/entities";

type ColumnBreakpoints =
  | {
      [key in "base" | "sm" | "md" | "lg" | "xl"]?: number;
    }
  | number
  | number[];

interface MovieGridProps {
  columns: ColumnBreakpoints;
  source: "movie_listing" | "more_like_this" | "by_actor";
  movie_id?: number;
  actor_id?: number;
  genre_id?: number;
}

// Memoized skeleton components to prevent unnecessary re-renders
const MovieSkeletonGrid = React.memo(
  ({ columns, count }: { columns: ColumnBreakpoints; count: number }) => {
    const skeletonsArray = Array.from({ length: count }, (_, i) => i + 1);
    return (
      <SimpleGrid columns={columns} spacing={3} padding={1}>
        {skeletonsArray.map((key) => (
          <MovieCardContainer key={key}>
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
    const scrollContainerRef = useRef<HTMLDivElement>(null);

    // Track URL search params to reset state when filters change
    const searchParams = useSearchParams();

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

    const { data, isLoading, fetchNextPage, hasNextPage, updateMovie, error } =
      useMovies({
        source,
        movie_id: safeIds.movieId,
        actor_id: safeIds.actorId,
        genre_id: safeIds.genreId,
      });

    const breakpointColumns = useBreakpointValue(
      columns as Record<string, number>
    );

    // Memoize the skeleton counts
    const skeletonCounts = useMemo(() => {
      const numSkeletons =
        typeof breakpointColumns === "number" ? breakpointColumns : 4;
      return {
        initial: numSkeletons * 6,
        next: 2 * numSkeletons - (100 % numSkeletons),
      };
    }, [breakpointColumns]);

    // Reset initial load state when URL params change
    useEffect(() => {
      setInitialLoadComplete(false);
    }, [searchParams]);

    // Calculate screen capacity on mount and resize - memoized calculation
    useEffect(() => {
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

    // Memoize fetchNextPage handler to prevent recreating on every render
    const handleFetchNextPage = useCallback(async () => {
      if (!fetchNextPage || loadingNextPage) return;

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
          updateMovie(movie);
        }
      },
      [updateMovie]
    );

    // Prefetch logic to ensure screen has enough content
    useEffect(() => {
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
        // If current count doesn't fill screen and we can load more
        if (fetchedMoviesCount < screenItemCapacity) {
          // Fetch more content
          handleFetchNextPage().then(() => {
            // After loading, check if we need to mark initial load as complete
            if (fetchedMoviesCount >= screenItemCapacity || !hasNextPage) {
              setInitialLoadComplete(true);
            }
          });
        } else {
          // We already have enough content
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
      console.error("Error fetching movies:", error);
      return <Text>Error loading movies. Please try again later.</Text>;
    }

    // Handle loading state
    if (isLoading) {
      return (
        <MovieSkeletonGrid columns={columns} count={skeletonCounts.initial} />
      );
    }

    // Handle empty states
    if (
      !data ||
      !data.pages ||
      data.pages.length === 0 ||
      fetchedMoviesCount === 0
    ) {
      return <Text>No movies found</Text>;
    }

    return (
      <Box ref={scrollContainerRef}>
        <InfiniteScroll
          dataLength={fetchedMoviesCount}
          next={handleFetchNextPage}
          hasMore={!!hasNextPage}
          loader={
            loadingNextPage ? (
              <MovieSkeletonGrid
                columns={columns}
                count={skeletonCounts.next}
              />
            ) : null
          }
          scrollThreshold={0.8}
          endMessage={
            <Text textAlign="center" py={4}>
              No more movies to load
            </Text>
          }
        >
          <SimpleGrid columns={columns} spacing={3} padding={1}>
            {movieList}
          </SimpleGrid>
        </InfiniteScroll>
        <ScrollToTopButton />
      </Box>
    );
  }
);

MovieGrid.displayName = "MovieGrid";

export default MovieGrid;
