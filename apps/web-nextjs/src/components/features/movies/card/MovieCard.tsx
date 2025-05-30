import { Movie } from "@/domain/entities";
import { useAuth } from "@/services/hooks";
import { useMovieInteractions } from "@/services/hooks/domain/movie/useMovieInteractions";
import { Box, Card, Image, useColorModeValue } from "@chakra-ui/react";
import Link from "next/link";
import { useEffect } from "react";
import { createLogger } from "@/utils/logging";
import MovieQuickAction from "./MovieQuickAction";
import MovieRatingIndicator from "./MovieRatingIndicator";
import { getPosterUrl } from "@/utils/media";

// Create logger for this component
const logger = createLogger("MovieCard");

interface MovieCardProps {
  movie: Movie;
  onMovieUpdate: (movie: Movie) => void; // Keep for compatibility but not used
}

const MovieCard = ({ movie }: MovieCardProps) => {
  const { user } = useAuth();
  const bgColor = useColorModeValue("bg.secondary", "bg.tertiary");

  // Use the same interaction hook pattern as movie details
  const movieInteractions = useMovieInteractions({
    movieId:
      typeof movie.id === "number" ? movie.id : parseInt(String(movie.id)),
    movie,
    additionalInvalidateKeys: ["home_page", "search", "infinite-search"],
  });

  // Log component rendering
  useEffect(() => {
    logger.debug(`Rendering MovieCard for: ${movie.title} (ID: ${movie.id})`);
  }, [movie.id, movie.title]);

  return (
    <Box
      position="relative"
      bg={bgColor}
      borderRadius={5}
      boxShadow="lg"
      overflow="hidden"
    >
      <Card
        direction={{ base: "row", md: "row" }}
        overflow="hidden"
        borderRadius={5}
      >
        <Box
          width="100%"
          position="relative"
          display="flex"
          flexDirection="column"
        >
          <Link href={`/movies/${movie.id}`} style={{ textDecoration: "none" }}>
            <Image
              borderRadius={5}
              zIndex={1}
              objectFit="cover"
              width="100%"
              height="100%"
              aspectRatio="2 / 3"
              src={
                getPosterUrl(movie.poster_path as string) ||
                (movie.poster_url as string)
              }
              alt={`${movie.title} Poster`}
            />
          </Link>

          {/* Modular rating indicator component */}
          <MovieRatingIndicator
            rating={
              typeof movie.imdb_rating === "number" ? movie.imdb_rating : null
            }
          />

          {user && (
            <Box
              position="absolute"
              right={0}
              top={0}
              height="100%"
              width="25%"
              display="flex"
              flexDirection="column"
              justifyContent="space-between"
              padding={0}
              className="quick-action"
            >
              <MovieQuickAction
                movie={movie}
                toggleFunctions={{
                  toggleWatched: () =>
                    movieInteractions.toggleWatched(undefined),
                  toggleLiked: () => movieInteractions.toggleLiked(undefined),
                  toggleWatchlist: () =>
                    movieInteractions.toggleWatchlist(undefined),
                }}
              />
            </Box>
          )}
        </Box>
      </Card>
    </Box>
  );
};

export default MovieCard;
