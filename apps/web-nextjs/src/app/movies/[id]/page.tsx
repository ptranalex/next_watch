"use client";

import React, { useCallback, useEffect } from "react";
import { useAuth, useMovie, useParams } from "@/hooks";
import { Movie } from "@/domain/entities";
import MovieDetailView from "@/components/features/movies/detail/MovieDetailView";
import { createLogger } from "@/utils/logging";
import { useResponsive } from "@/providers/ResponsiveContext";

// Create logger for this component
const logger = createLogger("MovieDetailPage");

// Force dynamic to ensure latest movie data is fetched
export const dynamic = "force-dynamic";

interface MovieDetailPageProps {
  params: Promise<{ id: string }> | { id: string };
}

/**
 * Movie detail page component
 * Displays a movie's details, with states for error and not found
 */
const MovieDetailPage = ({ params }: MovieDetailPageProps) => {
  // Log component initialization
  logger.debug("MovieDetailPage initializing");

  // Use our custom hook to handle params unwrapping
  const resolvedParams = useParams(params);
  const movieId = resolvedParams?.id ? Number(resolvedParams.id) : 0;

  // Use the centralized responsive context instead of direct media queries
  const { isMobile, isHydrated } = useResponsive();

  // Log the extracted movie ID
  useEffect(() => {
    if (isHydrated) {
      logger.info(`Rendering movie detail page for ID: ${movieId}`);
    }
  }, [movieId, isHydrated]);

  const { isAuthenticated } = useAuth();

  const {
    movie,
    isLoading,
    error,
    toggleWatched,
    toggleLiked,
    toggleWatchlist,
  } = useMovie(movieId);

  // Log movie data and errors
  useEffect(() => {
    if (isHydrated) {
      if (error) {
        logger.error(`Error loading movie ${movieId}:`, error);
      } else if (movie) {
        logger.info(`Movie data loaded: ${movie.title} (ID: ${movieId})`);
      }
    }
  }, [movie, error, movieId, isHydrated]);

  // Function to update movie from UI interactions (memoized)
  const updateMovie = useCallback(
    (updatedMovie: Movie) => {
      if (!movie) return;

      if (updatedMovie.watched !== movie.watched) {
        logger.debug(
          `Toggling watched status for movie ${movie.id}: ${!movie.watched}`
        );
        toggleWatched();
      } else if (updatedMovie.liked !== movie.liked) {
        logger.debug(
          `Toggling liked status for movie ${movie.id}: ${!movie.liked}`
        );
        toggleLiked();
      } else if (updatedMovie.in_watchlist !== movie.in_watchlist) {
        logger.debug(
          `Toggling watchlist status for movie ${
            movie.id
          }: ${!movie.in_watchlist}`
        );
        toggleWatchlist();
      }
    },
    [movie, toggleWatched, toggleLiked, toggleWatchlist]
  );

  // Render movie details (loading state handled by loading.tsx)
  return (
    <>
      {movie && (
        <MovieDetailView
          movie={movie}
          isSignedIn={isAuthenticated}
          onUpdateMovie={updateMovie}
        />
      )}
    </>
  );
};

export default MovieDetailPage;
