import {
  ActorsGallery,
  MovieAttributes,
  RatingGroup,
  MovieDetailViewProps,
} from "@/components/features/movies/detail";
import { ExpandableText } from "@/components/ui/molecules/display";
import { FEATURES } from "@/config/features";
import { createLogger } from "@/utils/logging";
import { Box, GridItem, Heading, SimpleGrid, Text } from "@chakra-ui/react";
import dynamic from "next/dynamic";
import React, { Suspense, useEffect, useMemo } from "react";
import { movieUtils } from "@/utils/movie/movieDataUtils";
import { ErrorBoundary } from "@/components/ui/molecules/feedback";
import MovieActionControls from "./MovieActionControls";
import MovieGrid from "@/components/features/movies/grid/MovieGrid";
import { Movie } from "@/domain/entities";

// Create logger for this component
const logger = createLogger("MobileMovieDetailView");

// Placeholder component for when the TrailerCard fails to load
const TrailerFallback = () => (
  <Box
    height="300px"
    width="100%"
    bg="bg.tertiary"
    display="flex"
    alignItems="center"
    justifyContent="center"
  >
    <Text color="text.tertiary">Trailer unavailable</Text>
  </Box>
);

// Lazy load non-critical components with error boundary
const TrailerCard = dynamic(
  () => import("@/components/features/movies/detail/TrailerCard"),
  {
    loading: () => {
      logger.debug("Loading trailer dynamically");
      return (
        <Box
          height="300px"
          width="100%"
          bg="bg.tertiary"
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <Text>Loading trailer...</Text>
        </Box>
      );
    },
    ssr: false,
  }
);

/**
 * Mobile version of the movie detail view with optimized layout for smaller screens
 */
const MobileMovieDetailView: React.FC<
  MovieDetailViewProps & { similarMovies?: Movie[] }
> = ({ movie, isSignedIn, onUpdateMovie, similarMovies = [] }) => {
  // Log component initialization
  useEffect(() => {
    logger.info(
      `Rendering mobile movie detail view for: ${movie.title} (ID: ${movie.id})`
    );
    logger.debug("Mobile movie data:", {
      movieId: movie.id,
      title: movie.title,
      hasTrailers: !!movie.trailers,
      trailersLength: movie.trailers?.length || 0,
      trailers: movie.trailers,
      hasCast: !!movie.cast,
      castLength: movie.cast?.length || 0,
      similarMoviesCount: similarMovies.length,
    });
  }, [movie.id, movie.title, movie.trailers, movie.cast, similarMovies.length]);

  // Memoize values to prevent recalculation
  const movieId = React.useMemo(() => movieUtils.getMovieId(movie), [movie]);
  const releaseYear = React.useMemo(
    () => movieUtils.getReleaseYear(movie),
    [movie]
  );
  const genres = React.useMemo(() => movieUtils.renderGenres(movie), [movie]);

  // For performance - extract only the needed rating data
  const ratings = React.useMemo(
    () => movieUtils.extractRatings(movie),
    [movie]
  );

  // Format cast data for ActorsGallery
  const castData = useMemo(() => {
    return {
      cast:
        movie.cast?.map((actor) => ({
          id: actor.id,
          name: actor.name,
          actor_id: actor.id,
          profile_path: actor.profile_path || "",
          character: actor.character || "",
        })) || [],
    };
  }, [movie.cast]);

  const overview = typeof movie.overview === "string" ? movie.overview : "";

  return (
    <>
      <SimpleGrid columns={1} spacing={5} paddingY={3} pb={20}>
        {/* Main content area */}
        <GridItem>
          <Box marginBottom={5} marginRight={-5} marginLeft={-5}>
            <ErrorBoundary
              fallback={<TrailerFallback />}
              componentName="TrailerCard"
            >
              <Suspense fallback={<TrailerFallback />}>
                <TrailerCard movieId={movieId} trailers={movie.trailers} />
              </Suspense>
            </ErrorBoundary>
          </Box>

          {/* Title and basic info */}
          <Heading marginBottom={2} fontSize="xl">
            {movieUtils.renderText(movie.title)}
          </Heading>

          <Text fontSize="md" marginBottom={1}>
            {releaseYear} • {movieUtils.renderText(movie.rated)} •{" "}
            {movieUtils.renderText(movie.runtime)}
          </Text>

          <Text fontSize="md" marginBottom={5}>
            {genres}
          </Text>

          {/* Ratings */}
          <Box marginBottom={5}>
            <ErrorBoundary
              fallback={<Text>Rating unavailable</Text>}
              componentName="RatingGroup"
            >
              <RatingGroup movie={ratings} scale_up={1} />
            </ErrorBoundary>
          </Box>

          {/* Movie overview */}
          <ExpandableText>{overview}</ExpandableText>

          {/* Actors gallery */}
          <Box width="100%" mt={3}>
            <ErrorBoundary
              fallback={<Text>Unable to load actors</Text>}
              componentName="ActorsGallery"
            >
              {movie.cast && movie.cast.length > 0 ? (
                <ActorsGallery movieId={movieId} castData={castData} />
              ) : (
                <Text fontSize="sm" color="text.tertiary">
                  No cast information available
                </Text>
              )}
            </ErrorBoundary>
          </Box>

          {/* Movie attributes */}
          <ErrorBoundary
            fallback={<Text>Details unavailable</Text>}
            componentName="MovieAttributes"
          >
            <MovieAttributes movie={movie} />
          </ErrorBoundary>

          {/* Similar movies */}
          {FEATURES.SHOW_MORE_LIKE_THIS && similarMovies.length > 0 && (
            <>
              <Heading size="md" marginBottom={3} marginTop={6}>
                More Like This
              </Heading>
              <ErrorBoundary
                fallback={<Text>Similar movies unavailable</Text>}
                componentName="SimilarMovies"
              >
                <MovieGrid
                  movies={similarMovies}
                  totalMovies={similarMovies.length}
                  fetchedMoviesCount={similarMovies.length}
                  isLoading={false}
                  isFetchingNextPage={false}
                  hasNextPage={false}
                  columns={{ base: 2, sm: 3 }}
                  source="similar_movies"
                  emptyMessage="No similar movies found"
                />
              </ErrorBoundary>
            </>
          )}
        </GridItem>
      </SimpleGrid>

      {/* Use MovieActionControls component */}
      {isSignedIn && onUpdateMovie && (
        <MovieActionControls movie={movie} onUpdateMovie={onUpdateMovie} />
      )}
    </>
  );
};

export default MobileMovieDetailView;
