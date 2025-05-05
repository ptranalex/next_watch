"use client";

import { Box, SimpleGrid, Text, useBreakpointValue } from "@chakra-ui/react";
import React, { useState, useEffect, useRef } from "react";
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

const MovieGrid = ({
  columns,
  source,
  movie_id,
  actor_id,
  genre_id,
}: MovieGridProps) => {
  const [loadingNextPage, setLoadingNextPage] = useState(false);
  const [screenItemCapacity, setScreenItemCapacity] = useState(0);
  const [initialLoadComplete, setInitialLoadComplete] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Track URL search params to reset state when filters change
  const searchParams = useSearchParams();

  const safeMovieId =
    typeof movie_id === "number" && movie_id > 0 ? movie_id : undefined;
  const safeActorId =
    typeof actor_id === "number" && actor_id > 0 ? actor_id : undefined;
  const safeGenreId =
    typeof genre_id === "number" && genre_id > 0 ? genre_id : undefined;

  const { data, isLoading, fetchNextPage, hasNextPage, updateMovie, error } =
    useMovies({
      source,
      movie_id: safeMovieId,
      actor_id: safeActorId,
      genre_id: safeGenreId,
    });

  const breakpointColumns = useBreakpointValue(
    columns as Record<string, number>
  );

  const numSkeletons =
    typeof breakpointColumns === "number" ? breakpointColumns : 4;
  const skeletonsArray = Array.from(
    { length: numSkeletons * 6 },
    (_, i) => i + 1
  );
  const nextSkeletonsArray = Array.from(
    { length: 2 * numSkeletons - (100 % numSkeletons) },
    (_, i) => i + 1
  );

  // Reset initial load state when URL params change
  useEffect(() => {
    setInitialLoadComplete(false);
  }, [searchParams]);

  // Calculate screen capacity on mount and resize
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

    // Recalculate on resize
    window.addEventListener("resize", calculateCapacity);
    return () => window.removeEventListener("resize", calculateCapacity);
  }, [breakpointColumns]);

  // Handle next page loading with loading state
  const handleFetchNextPage = async () => {
    if (!fetchNextPage || loadingNextPage) return;

    setLoadingNextPage(true);
    await fetchNextPage();
    setLoadingNextPage(false);
  };

  // Calculate fetchedMoviesCount when data is available
  const fetchedMoviesCount =
    data?.pages?.reduce(
      (total, page) =>
        total + (Array.isArray(page.movies) ? page.movies.length : 0),
      0
    ) || 0;

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
  ]);

  if (error) {
    console.error("Error fetching movies:", error);
    return <Text>Error loading movies. Please try again later.</Text>;
  }

  if (isLoading) {
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

  if (!data || !data.pages || data.pages.length === 0) {
    return <Text>No movies found</Text>;
  }

  if (fetchedMoviesCount === 0) {
    return <Text>No movies found</Text>;
  }

  const handleMovieUpdate = (movie: Movie) => {
    if (typeof updateMovie === "function") {
      updateMovie(movie);
    }
  };

  return (
    <Box ref={scrollContainerRef}>
      <InfiniteScroll
        dataLength={fetchedMoviesCount}
        next={handleFetchNextPage}
        hasMore={!!hasNextPage}
        loader={
          loadingNextPage ? (
            <SimpleGrid columns={columns} spacing={3} padding={1}>
              {nextSkeletonsArray.map((key) => (
                <MovieCardContainer key={key}>
                  <MovieCardSkeleton />
                </MovieCardContainer>
              ))}
            </SimpleGrid>
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
          {data?.pages.map((page, index) => (
            <React.Fragment key={index}>
              {Array.isArray(page.movies) &&
                page.movies.map((movie: Movie) =>
                  movie && typeof movie === "object" && movie.id ? (
                    <MovieCardContainer key={String(movie.id)}>
                      <MovieCard
                        movie={movie}
                        onMovieUpdate={handleMovieUpdate}
                      />
                    </MovieCardContainer>
                  ) : null
                )}
            </React.Fragment>
          ))}
        </SimpleGrid>
      </InfiniteScroll>
      <ScrollToTopButton />
    </Box>
  );
};

export default MovieGrid;
