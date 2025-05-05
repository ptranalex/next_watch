import React, { Suspense, useEffect, useState } from "react";
import {
  Box,
  Heading,
  Image,
  SimpleGrid,
  GridItem,
  Stack,
  Text,
  HStack,
  Spinner,
} from "@chakra-ui/react";
import { Movie, Actor, Genre } from "@/domain/entities";
import MovieAttributes from "./MovieAttributes";
import MovieQuickAction from "./MovieQuickAction";
import RatingGroup from "./RatingGroup";
import ExpandableText from "../utils/ExpandableText";
import ActorsGallery from "./ActorsGallery";
import { FEATURES } from "@/config/features";
import MovieGrid from "../home/MovieGrid";
import dynamic from "next/dynamic";

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

// Helper functions for type safety
const getMovieId = (movie: Movie): number => {
  return typeof movie.id === "number" ? movie.id : 0;
};

const getActors = (movie: Movie): Actor[] => {
  if (!movie.actors || !Array.isArray(movie.actors)) return [];
  return movie.actors.filter(
    (actor): actor is Actor =>
      typeof actor === "object" && actor !== null && "name" in actor
  );
};

const getReleaseYear = (movie: Movie): string => {
  if (!movie.release_date) return "";
  try {
    return new Date(movie.release_date.toString()).getFullYear().toString();
  } catch {
    return "";
  }
};

const renderText = (value: unknown): string => {
  if (value === undefined || value === null) return "";
  return String(value);
};

const renderGenres = (movie: Movie): string => {
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
};

const MovieDetailView: React.FC<MovieDetailViewProps> = ({
  movie,
  isSignedIn,
  isSmallerScreen,
  onUpdateMovie,
}) => {
  // State to track if components have loaded successfully
  const [trailerLoaded, setTrailerLoaded] = useState(false);

  // Attempt to load components safely
  useEffect(() => {
    try {
      setTrailerLoaded(true);
    } catch (error) {
      console.error("Error loading components:", error);
    }
  }, []);

  return (
    <SimpleGrid columns={{ base: 1, md: 3 }} spacing={5}>
      {!isSmallerScreen && (
        <GridItem display="flex" justifyContent="flex-end">
          <Box maxWidth={280}>
            <Stack alignItems="flex-end">
              <Image
                float={{ base: "left", lg: "right" }}
                src={
                  typeof movie.poster_url === "string" ? movie.poster_url : ""
                }
                alt={
                  typeof movie.title === "string" ? movie.title : "Movie poster"
                }
              />
              <ErrorBoundary fallback={<Text>Unable to load actors</Text>}>
                <ActorsGallery actors={getActors(movie)} />
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
              <TrailerCard movieId={getMovieId(movie)} />
            </Suspense>
          </ErrorBoundary>
        </Box>
        <Heading marginBottom={2}>{renderText(movie.title)}</Heading>
        <Text fontSize="md" marginBottom={1}>
          {getReleaseYear(movie)} • {renderText(movie.rated)} •{" "}
          {renderText(movie.runtime)}
        </Text>
        <Text fontSize="md" marginBottom={5}>
          {renderGenres(movie)}
        </Text>
        <Box marginBottom={5}>
          <ErrorBoundary fallback={<Text>Rating unavailable</Text>}>
            <RatingGroup
              movie={{
                imdb_rating:
                  typeof movie.imdb_rating === "number"
                    ? movie.imdb_rating
                    : null,
                rotten_tomatoes_rating:
                  typeof movie.rotten_tomatoes_rating === "number"
                    ? movie.rotten_tomatoes_rating
                    : null,
                metacritic_rating:
                  typeof movie.metacritic_rating === "number"
                    ? movie.metacritic_rating
                    : null,
              }}
              scale_up={1.3}
            />
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
        <ExpandableText>
          {typeof movie.overview === "string" ? movie.overview : ""}
        </ExpandableText>
        {isSmallerScreen && (
          <Box width="50%" mt={3}>
            <ErrorBoundary fallback={<Text>Unable to load actors</Text>}>
              <ActorsGallery actors={getActors(movie)} />
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
                movie_id={getMovieId(movie)}
              />
            </ErrorBoundary>
          </>
        )}
      </GridItem>
    </SimpleGrid>
  );
};

export default MovieDetailView;
