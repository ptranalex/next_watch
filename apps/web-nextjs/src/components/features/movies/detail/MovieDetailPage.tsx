"use client";

import React, { useEffect, memo } from "react";
import { useAuth } from "@/services/hooks";
import { useMovieDetailPage } from "@/services/hooks/pages";
import DesktopMovieDetailView from "./DesktopMovieDetailView";
import MobileMovieDetailView from "@/components/mobile/features/movies/detail/MobileMovieDetailView";
import { createLogger } from "@/utils/logging";
import { useResponsive } from "@/providers/ResponsiveContext";

// Create logger for this component
const logger = createLogger("MovieDetailPage");

// Movie detail page props interface
export interface MovieDetailPageProps {
  /** Movie ID to display details for */
  movieId: number;
}

/**
 * MovieDetailPage component - Displays detailed information about a movie
 *
 * This is a feature-level component that contains all the business logic
 * for displaying movie details, handling user interactions, managing
 * optimistic updates, and selecting the appropriate layout (mobile/desktop).
 *
 * @param props - Component props
 * @param props.movieId - The ID of the movie to display details for
 */
const MovieDetailPage = memo(({ movieId }: MovieDetailPageProps) => {
  // Log component initialization
  logger.debug("MovieDetailPage initializing", { movieId });

  // Use our centralized responsive context for layout selection
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
    error,
    toggleWatched,
    toggleLiked,
    toggleWatchlist,
    updateMovieOptimistically,
    relatedMovies,
  } = useMovieDetailPage(movieId);

  logger.debug("MovieDetailPage", {
    movie,
    error,
    movieId,
    similarMoviesCount: relatedMovies?.length || 0,
  });

  // Log movie data and errors
  useEffect(() => {
    if (isHydrated) {
      if (error) {
        logger.error(`Error loading movie ${movieId}:`, error);
      } else if (movie) {
        logger.info(`Movie data loaded: ${movie.title} (ID: ${movieId})`);
        logger.info(`Similar movies loaded: ${relatedMovies?.length || 0}`);
      }
    }
  }, [movie, error, movieId, isHydrated, relatedMovies?.length]);

  // Log which layout is being rendered
  useEffect(() => {
    if (isHydrated && movie) {
      logger.info(
        `MovieDetailPage choosing ${
          isMobile ? "mobile" : "desktop"
        } layout for movie: ${movie.title}`
      );
    }
  }, [isMobile, isHydrated, movie]);

  // Validate movie ID
  if (!movieId || movieId <= 0 || isNaN(movieId)) {
    return (
      <div className="text-center py-10">
        <p>Invalid movie ID. Please select a valid movie.</p>
      </div>
    );
  }

  // Wait for movie data to load (loading state handled by loading.tsx)
  if (!movie) {
    return null;
  }

  // Prepare props for both mobile and desktop views
  const viewProps = {
    movie,
    isSignedIn: isAuthenticated,
    onUpdateMovie: updateMovieOptimistically,
    toggleFunctions: {
      toggleWatched,
      toggleLiked,
      toggleWatchlist,
    },
    similarMovies: relatedMovies || [],
  };

  // SSR-safe layout selection: always render desktop layout during SSR
  // Only switch to mobile layout after hydration if on mobile
  if (!isHydrated || !isMobile) {
    return (
      <DesktopMovieDetailView
        movie={movie}
        isSignedIn={isAuthenticated}
        toggleFunctions={{
          toggleWatched,
          toggleLiked,
          toggleWatchlist,
        }}
        similarMovies={relatedMovies || []}
      />
    );
  }

  // Only render mobile layout after hydration is complete and we've confirmed mobile device
  return <MobileMovieDetailView {...viewProps} />;
});

MovieDetailPage.displayName = "MovieDetailPage";

export default MovieDetailPage;
