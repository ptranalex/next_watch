import MovieGrid from "@/components/home/MovieGrid";
import ActorsGallery from "@/components/movieDetails/ActorsGallery";
import MovieAttributes from "@/components/movieDetails/MovieAttributes";
import MovieDetailBottomActionBar from "@/components/mobile/movieDetails/MovieDetailBottomActionBar";
import ExpandableText from "@/components/utils/ExpandableText";
import RatingGroup from "@/components/movieDetails/RatingGroup";
import { FEATURES } from "@/config/features";
import { createLogger } from "@/utils/logging";
import { Box, GridItem, Heading, SimpleGrid, Text } from "@chakra-ui/react";
import dynamic from "next/dynamic";
import React, { Suspense, useEffect } from "react";
import { MovieDetailViewProps } from "@/components/movieDetails/types";
import { movieUtils } from "@/utils/movie/movieDataUtils";
import ErrorBoundary from "@/components/utils/ErrorBoundary";

// Create logger for this component
const logger = createLogger("MobileMovieDetailView");

// Placeholder component for when the TrailerCard fails to load
const TrailerFallback = () => (
  <Box
    height="300px"
    width="100%"
    bg="gray.700"
    display="flex"
    alignItems="center"
    justifyContent="center"
  >
    <Text color="gray.400">Trailer unavailable</Text>
  </Box>
);

// Lazy load non-critical components with error boundary
const TrailerCard = dynamic(
  () => import("@/components/movieDetails/TrailerCard"),
  {
    loading: () => {
      logger.debug("Loading trailer dynamically");
      return (
        <Box
          height="300px"
          width="100%"
          bg="gray.700"
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
const MobileMovieDetailView: React.FC<MovieDetailViewProps> = ({
  movie,
  isSignedIn,
  onUpdateMovie,
}) => {
  // Log component initialization
  useEffect(() => {
    logger.info(
      `Rendering mobile movie detail view for: ${movie.title} (ID: ${movie.id})`
    );
  }, [movie.id, movie.title]);

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
    [movie.imdb_rating, movie.rotten_tomatoes_rating, movie.metacritic_rating]
  );

  // Safely extract poster URL and title
  const posterUrl =
    typeof movie.poster_url === "string" ? movie.poster_url : "";
  const title = typeof movie.title === "string" ? movie.title : "Movie poster";
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
                <TrailerCard movieId={movieId} />
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
              <ActorsGallery movieId={movieId} />
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
          {FEATURES.SHOW_MORE_LIKE_THIS && (
            <>
              <Heading size="md" marginBottom={2} marginTop={5}>
                More Like This
              </Heading>
              <ErrorBoundary
                fallback={<Text>Similar movies unavailable</Text>}
                componentName="SimilarMovies"
              >
                <MovieGrid
                  columns={{ base: 2, sm: 3 }}
                  source="more_like_this"
                  movie_id={movieId}
                />
              </ErrorBoundary>
            </>
          )}
        </GridItem>
      </SimpleGrid>

      {/* Bottom action bar - only show for signed in users */}
      {isSignedIn && (
        <MovieDetailBottomActionBar
          movie={movie}
          onUpdateMovie={onUpdateMovie}
        />
      )}
    </>
  );
};

export default MobileMovieDetailView;
