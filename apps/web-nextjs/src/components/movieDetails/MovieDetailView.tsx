import MovieGrid from "@/components/home/MovieGrid";
import ActorsGallery from "@/components/movieDetails/ActorsGallery";
import MovieAttributes from "@/components/movieDetails/MovieAttributes";
import MovieQuickAction from "@/components/movieDetails/MovieQuickAction";
import RatingGroup from "@/components/movieDetails/RatingGroup";
import ExpandableText from "@/components/utils/ExpandableText";
import { FEATURES } from "@/config/features";
import { Genre, Movie } from "@/domain/entities";
import {
  Box,
  GridItem,
  Heading,
  Image,
  SimpleGrid,
  Stack,
  Text,
} from "@chakra-ui/react";
import dynamic from "next/dynamic";
import React, { Suspense, memo } from "react";

// Placeholder component for when the TrailerCard fails to load
const TrailerFallback = memo(() => (
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
));
TrailerFallback.displayName = "TrailerFallback";

// Error boundary component for dynamic imports
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: React.ReactNode; fallback: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("Component error:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

// Lazy load non-critical components with error boundary
const TrailerCard = dynamic(() => import("./TrailerCard"), {
  loading: () => (
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
  ),
  ssr: false,
});

interface MovieDetailViewProps {
  movie: Movie;
  isSignedIn: boolean;
  isSmallerScreen: boolean;
  onUpdateMovie: (movie: Movie) => void;
}

/**
 * Utilities for safe movie data access with proper type checking
 */
const movieUtils = {
  /**
   * Safely extracts the movie ID as a number
   */
  getMovieId: (movie: Movie): number => {
    return typeof movie.id === "number" ? movie.id : 0;
  },

  /**
   * Extracts release year from date string
   */
  getReleaseYear: (movie: Movie): string => {
    if (!movie.release_date) return "";
    try {
      return new Date(movie.release_date.toString()).getFullYear().toString();
    } catch {
      return "";
    }
  },

  /**
   * Safely renders any value as a string
   */
  renderText: (value: unknown): string => {
    if (value === undefined || value === null) return "";
    return String(value);
  },

  /**
   * Formats movie genres as a comma-separated string
   */
  renderGenres: (movie: Movie): string => {
    if (!movie.genres || !Array.isArray(movie.genres)) return "N/A";
    return (
      movie.genres
        .filter(
          (genre): genre is Genre =>
            typeof genre === "object" && genre !== null && "name" in genre
        )
        .map((genre) => genre.name)
        .join(", ") || "N/A"
    );
  },
};

/**
 * The main component for displaying detailed movie information
 * Includes trailer, metadata, ratings, and interactive elements
 */
const MovieDetailView: React.FC<MovieDetailViewProps> = ({
  movie,
  isSignedIn,
  isSmallerScreen,
  onUpdateMovie,
}) => {
  // Memoize values to prevent recalculation
  const movieId = React.useMemo(() => movieUtils.getMovieId(movie), [movie]);
  const releaseYear = React.useMemo(
    () => movieUtils.getReleaseYear(movie),
    [movie]
  );
  const genres = React.useMemo(() => movieUtils.renderGenres(movie), [movie]);

  // For performance - extract only the needed rating data
  const ratings = React.useMemo(
    () => ({
      imdb_rating:
        typeof movie.imdb_rating === "number" ? movie.imdb_rating : null,
      rotten_tomatoes_rating:
        typeof movie.rotten_tomatoes_rating === "number"
          ? movie.rotten_tomatoes_rating
          : null,
      metacritic_rating:
        typeof movie.metacritic_rating === "number"
          ? movie.metacritic_rating
          : null,
    }),
    [movie.imdb_rating, movie.rotten_tomatoes_rating, movie.metacritic_rating]
  );

  // Safely extract poster URL and title
  const posterUrl =
    typeof movie.poster_url === "string" ? movie.poster_url : "";
  const title = typeof movie.title === "string" ? movie.title : "Movie poster";
  const overview = typeof movie.overview === "string" ? movie.overview : "";

  return (
    <SimpleGrid columns={{ base: 1, md: 3 }} spacing={5}>
      {!isSmallerScreen && (
        <GridItem display="flex" justifyContent="flex-end">
          <Box maxWidth={280}>
            <Stack alignItems="flex-end">
              <Image
                float={{ base: "left", lg: "right" }}
                src={posterUrl}
                alt={title}
              />
              <ErrorBoundary fallback={<Text>Unable to load actors</Text>}>
                <ActorsGallery movieId={movieId} />
              </ErrorBoundary>
            </Stack>
          </Box>
        </GridItem>
      )}
      <GridItem colSpan={2}>
        <Box
          marginBottom={5}
          marginRight={{ base: -5, md: "auto" }}
          marginLeft={{ base: -5, md: "auto" }}
        >
          <ErrorBoundary fallback={<TrailerFallback />}>
            <Suspense fallback={<TrailerFallback />}>
              <TrailerCard movieId={movieId} />
            </Suspense>
          </ErrorBoundary>
        </Box>
        <Heading marginBottom={2}>{movieUtils.renderText(movie.title)}</Heading>
        <Text fontSize="md" marginBottom={1}>
          {releaseYear} • {movieUtils.renderText(movie.rated)} •{" "}
          {movieUtils.renderText(movie.runtime)}
        </Text>
        <Text fontSize="md" marginBottom={5}>
          {genres}
        </Text>
        <Box marginBottom={5}>
          <ErrorBoundary fallback={<Text>Rating unavailable</Text>}>
            <RatingGroup movie={ratings} scale_up={1.3} />
          </ErrorBoundary>
        </Box>
        {isSignedIn && (
          <Box marginBottom={5}>
            <ErrorBoundary fallback={<Text>Actions unavailable</Text>}>
              <MovieQuickAction
                movie={movie}
                onMovieUpdate={onUpdateMovie}
                orientation="horizontal"
                size="md"
              />
            </ErrorBoundary>
          </Box>
        )}
        <ExpandableText>{overview}</ExpandableText>
        {isSmallerScreen && (
          <Box width="50%" mt={3}>
            <ErrorBoundary fallback={<Text>Unable to load actors</Text>}>
              <ActorsGallery movieId={movieId} />
            </ErrorBoundary>
          </Box>
        )}
        <ErrorBoundary fallback={<Text>Details unavailable</Text>}>
          <MovieAttributes movie={movie} />
        </ErrorBoundary>
        {FEATURES.SHOW_MORE_LIKE_THIS && (
          <>
            <Heading size="md" marginBottom={2} marginTop={5}>
              More Like This
            </Heading>
            <ErrorBoundary fallback={<Text>Similar movies unavailable</Text>}>
              <MovieGrid
                columns={{ base: 3, md: 3, lg: 4 }}
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

export default memo(MovieDetailView);
