"use client";

import { useMediaQuery } from "@chakra-ui/react";
import React, { useCallback, useEffect, useState } from "react";
import { useAuth, useMovie, useParams } from "@/hooks";
import { Movie } from "@/domain/entities";
import MovieDetailView from "@/components/movieDetails/MovieDetailView";
import MovieLayout from "@/components/layout/MovieLayout";
import MovieSkeleton from "@/components/movieDetails/MovieSkeleton";
import MovieErrorState from "@/components/movieDetails/MovieErrorState";
import MovieNotFoundState from "@/components/movieDetails/MovieNotFoundState";
import MovieInitialLoading from "@/components/movieDetails/MovieInitialLoading";

// Export dynamic to ensure server-side rendering works correctly
export const dynamic = "force-dynamic";

// Handle movie id parameter in a way compatible with Next.js
interface MovieDetailPageProps {
  params: Promise<{ id: string }> | { id: string };
}

/**
 * Movie detail page component
 * Displays a movie's details, with states for loading, error, and not found
 */
const MovieDetailPage = ({ params }: MovieDetailPageProps) => {
  const [isParamsLoading, setIsParamsLoading] = useState(true);

  // Use our custom hook to handle params unwrapping
  const resolvedParams = useParams(params);
  const movieId = resolvedParams?.id ? Number(resolvedParams.id) : null;

  // Track when params are resolved
  useEffect(() => {
    if (resolvedParams && Object.keys(resolvedParams).length > 0) {
      setIsParamsLoading(false);
    }
  }, [resolvedParams]);

  const { isAuthenticated } = useAuth();
  const [isSmallerScreen] = useMediaQuery("(max-width: 600px)");

  const {
    movie,
    isLoading: isMovieLoading,
    error,
    toggleWatched,
    toggleLiked,
    toggleWatchlist,
  } = useMovie(movieId || 0);

  // Function to update movie from UI interactions (memoized)
  const updateMovie = useCallback(
    (updatedMovie: Movie) => {
      if (!movie) return;

      if (updatedMovie.watched !== movie.watched) {
        toggleWatched();
      } else if (updatedMovie.liked !== movie.liked) {
        toggleLiked();
      } else if (updatedMovie.in_watchlist !== movie.in_watchlist) {
        toggleWatchlist();
      }
    },
    [movie, toggleWatched, toggleLiked, toggleWatchlist]
  );

  // Show initial loading state while waiting for params to resolve
  if (isParamsLoading || movieId === null) {
    return (
      <MovieLayout>
        <MovieInitialLoading />
      </MovieLayout>
    );
  }

  // Show loading state while fetching movie data
  if (isMovieLoading) {
    return (
      <MovieLayout>
        <MovieSkeleton isSmallerScreen={isSmallerScreen} />
      </MovieLayout>
    );
  }

  // Handle error state
  if (error) {
    return (
      <MovieLayout>
        <MovieErrorState error={error as string} />
      </MovieLayout>
    );
  }

  // Handle movie not found
  if (!movie) {
    return (
      <MovieLayout>
        <MovieNotFoundState />
      </MovieLayout>
    );
  }

  // Render movie details
  return (
    <MovieLayout>
      <MovieDetailView
        movie={movie}
        isSignedIn={isAuthenticated}
        isSmallerScreen={isSmallerScreen}
        onUpdateMovie={updateMovie}
      />
    </MovieLayout>
  );
};

export default MovieDetailPage;
