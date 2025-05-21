import React, { useState, useEffect } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { useResponsive } from "@/context/ResponsiveContext";
import { fetchData } from "@/services/api";
import { Movie } from "@/domain/entities";
import MovieGrid from "@/components/home/MovieGrid";
import MobileMovieList from "@/components/mobile/movieCard/MobileMovieList";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("ResponsiveMovieGrid");

interface ResponsiveMovieGridProps {
  columns?: {
    base?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  source: string;
}

/**
 * ResponsiveMovieGrid component
 * Renders either a grid (desktop) or list (mobile) view of movies
 * Automatically determines the best layout based on device
 */
const ResponsiveMovieGrid: React.FC<ResponsiveMovieGridProps> = ({
  columns,
  source,
}) => {
  const { isMobile } = useResponsive();
  const [movies, setMovies] = useState<Movie[]>([]);

  // Fetch movies from the API
  const { data, isLoading, error } = useInfiniteQuery({
    queryKey: [source],
    queryFn: ({ pageParam = 1 }) =>
      fetchData(`/api/v1/${source}?page=${pageParam}`),
    getNextPageParam: (lastPage) =>
      lastPage.has_more ? lastPage.page + 1 : undefined,
  });

  // Update movies when data changes
  useEffect(() => {
    if (data) {
      const allMovies = data.pages.flatMap((page) => page.results);
      logger.debug(`Loaded ${allMovies.length} movies for ${source}`);
      setMovies(allMovies);
    }
  }, [data, source]);

  // Handle movie updates (liked, watchlist, watched status)
  const handleMovieUpdate = (updatedMovie: Movie) => {
    const updatedMovies = movies.map((movie) =>
      movie.id === updatedMovie.id ? updatedMovie : movie
    );
    setMovies(updatedMovies);
  };

  // Determine which component to render based on device
  if (isMobile) {
    logger.debug("Rendering mobile movie list");
    return (
      <MobileMovieList
        movies={movies}
        isLoading={isLoading}
        error={error as Error | null}
        onMovieUpdate={handleMovieUpdate}
      />
    );
  }

  logger.debug("Rendering desktop movie grid");
  return <MovieGrid columns={columns} source={source} />;
};

export default ResponsiveMovieGrid;
