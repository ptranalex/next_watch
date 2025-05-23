import React, { useEffect } from "react";
import {
  Box,
  GridItem,
  Heading,
  Image,
  SimpleGrid,
  Stack,
  Text,
} from "@chakra-ui/react";
import { createLogger } from "@/utils/logging";
import { movieUtils } from "@/utils/movie/movieDataUtils";
import { FEATURES } from "@/config/features";
import dynamic from "next/dynamic";
import { Suspense } from "react";
import { ErrorBoundary } from "@/components/ui/molecules/feedback";
import ActorsGallery from "./ActorsGallery";
import MovieAttributes from "./MovieAttributes";
import MovieQuickAction from "./MovieQuickAction";
import RatingGroup from "./RatingGroup";
import { ExpandableText } from "@/components/ui/molecules/display";
import MovieGrid from "@/components/features/movies/grid/MovieGrid";
import { MovieDetailViewProps } from "./types";

// Create logger for this component
const logger = createLogger("DesktopMovieDetailView");

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
const TrailerCard = dynamic(() => import("./TrailerCard"), {
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
});

/**
 * Desktop/tablet version of the movie detail view
 */
const DesktopMovieDetailView: React.FC<MovieDetailViewProps> = ({
  movie,
  isSignedIn,
  onUpdateMovie,
}) => {
  // Log component initialization
  useEffect(() => {
    logger.info(
      `Rendering desktop movie detail view for: ${movie.title} (ID: ${movie.id})`
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
    [movie]
  );

  // Safely extract poster URL and title
  const posterUrl =
    typeof movie.poster_url === "string" ? movie.poster_url : "";
  const title = typeof movie.title === "string" ? movie.title : "Movie poster";
  const overview = typeof movie.overview === "string" ? movie.overview : "";

  return (
    <SimpleGrid columns={{ base: 1, md: 3 }} spacing={5} paddingY={5}>
      {/* Poster image */}
      <GridItem display="flex" justifyContent="flex-end">
        <Box maxWidth={280}>
          <Stack alignItems="flex-end">
            <Image
              float={{ base: "left", lg: "right" }}
              src={posterUrl}
              alt={title}
            />
            <ErrorBoundary
              fallback={<Text>Unable to load actors</Text>}
              componentName="ActorsGallery"
            >
              <ActorsGallery movieId={movieId} />
            </ErrorBoundary>
          </Stack>
        </Box>
      </GridItem>

      {/* Main content area */}
      <GridItem colSpan={{ base: 1, md: 2 }}>
        <Box
          marginBottom={5}
          marginRight={{ base: -5, md: "auto" }}
          marginLeft={{ base: -5, md: "auto" }}
        >
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
        <Heading marginBottom={2} fontSize={{ base: "xl", md: "2xl" }}>
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
            <RatingGroup movie={ratings} scale_up={1.3} />
          </ErrorBoundary>
        </Box>

        {/* User actions */}
        {isSignedIn && (
          <Box marginBottom={5}>
            <ErrorBoundary
              fallback={<Text>Actions unavailable</Text>}
              componentName="MovieQuickAction"
            >
              <MovieQuickAction
                movie={movie}
                onMovieUpdate={onUpdateMovie}
                orientation="horizontal"
                size="md"
              />
            </ErrorBoundary>
          </Box>
        )}

        {/* Movie overview */}
        <ExpandableText>{overview}</ExpandableText>

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
            <Heading size="lg" marginBottom={2} marginTop={5}>
              More Like This
            </Heading>
            <ErrorBoundary
              fallback={<Text>Similar movies unavailable</Text>}
              componentName="SimilarMovies"
            >
              <MovieGrid
                columns={{ base: 2, sm: 3, md: 3, lg: 4 }}
                source="more_like_this"
                movie_id={movieId}
              />
            </ErrorBoundary>
          </>
        )}
      </GridItem>
    </SimpleGrid>
  );
};

export default DesktopMovieDetailView;
