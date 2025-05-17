import MovieQuickAction from "@/components/movieCard/MovieQuickAction";
import { Movie } from "@/domain/entities";
import { useAuth } from "@/hooks";
import { fetchData, userInteractionAPI } from "@/services/api";
import {
  Box,
  Card,
  Icon,
  Image,
  useColorModeValue,
  useToast,
} from "@chakra-ui/react";
import { useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useEffect, useState } from "react";
import { HiMiniStar } from "react-icons/hi2";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("MovieCard");

interface Props {
  movie: Movie;
  onMovieUpdate: (movie: Movie) => void;
}

const MovieCard = ({ movie, onMovieUpdate }: Props) => {
  const { user } = useAuth();
  const bgColor = useColorModeValue("gray.100", "gray.800");
  const [isHovered, setIsHovered] = useState(false);
  const queryClient = useQueryClient();
  const toast = useToast();

  // Log component rendering
  useEffect(() => {
    logger.debug(`Rendering MovieCard for: ${movie.title} (ID: ${movie.id})`);
  }, [movie.id, movie.title]);

  // This handler is called by the MovieQuickAction child component
  const handleMovieUpdate = async (updatedMovie: Movie) => {
    try {
      logger.info(`Updating movie ${movie.id} (${movie.title})`, {
        watched: `${movie.watched} → ${updatedMovie.watched}`,
        liked: `${movie.liked} → ${updatedMovie.liked}`,
        in_watchlist: `${movie.in_watchlist} → ${updatedMovie.in_watchlist}`,
      });

      // First update local state for immediate UI feedback
      onMovieUpdate(updatedMovie);

      // Ensure movie.id is a number
      if (typeof movie.id !== "number") {
        logger.error(`Invalid movie ID for ${movie.title}`);
        throw new Error("Invalid movie ID");
      }

      // Then update the server state using the correct API endpoints
      if (updatedMovie.watched !== movie.watched) {
        logger.debug(`Calling toggleWatched API for movie ${movie.id}`);
        await userInteractionAPI.toggleWatched(movie.id);
      }

      if (updatedMovie.liked !== movie.liked) {
        logger.debug(`Calling toggleLiked API for movie ${movie.id}`);
        await userInteractionAPI.toggleLiked(movie.id);
      }

      if (updatedMovie.in_watchlist !== movie.in_watchlist) {
        logger.debug(`Calling toggleWatchlist API for movie ${movie.id}`);
        await userInteractionAPI.toggleWatchlist(movie.id);
      }

      // Invalidate relevant queries to refetch data
      logger.debug(`Invalidating queries for movie ${movie.id}`);
      queryClient.invalidateQueries(["movie", movie.id]);
    } catch (error) {
      logger.error(
        `Failed to update movie interaction for ${movie.id}:`,
        error
      );
      toast({
        title: "Update failed",
        description: "Failed to update movie status. Please try again.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });

      // Revert the local state on error
      logger.debug(`Reverting local state for movie ${movie.id}`);
      onMovieUpdate(movie);
    }
  };

  const getColor = (value: number | undefined) => {
    if (!value) return "hidden";

    if (value >= 8.0) {
      return "***REMOVED***FFC107";
    } else if (value >= 7.0) {
      return "***REMOVED***00E676";
    } else if (value >= 6.0) {
      return "***REMOVED***82B1FF";
    }
    return "hidden";
  };

  const color = getColor(
    typeof movie.imdb_rating === "number" ? movie.imdb_rating : undefined
  );

  const prefetchMovieData = () => {
    if (typeof movie.id !== "number") return;

    logger.debug(`Prefetching data for movie ${movie.id}`);

    queryClient.prefetchQuery({
      queryKey: ["movie", movie.id],
      queryFn: () => fetchData(`/api/v1/movies/${movie.id}`),
    });

    queryClient.prefetchQuery({
      queryKey: ["movie", movie.id, "trailers"],
      queryFn: () => fetchData(`/api/v1/movies/${movie.id}/trailers`),
    });
  };

  return (
    <Box
      position="relative"
      bg={bgColor}
      borderRadius="0"
      boxShadow="lg"
      overflow="hidden"
      onMouseEnter={() => {
        setIsHovered(true);
        logger.debug(`MovieCard hovered: ${movie.id} (${movie.title})`);
      }}
      onMouseLeave={() => {
        setIsHovered(false);
        logger.debug(`MovieCard hover exited: ${movie.id} (${movie.title})`);
      }}
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
          <Link
            href={`/movies/${movie.id}`}
            style={{ textDecoration: "none" }}
            onMouseEnter={prefetchMovieData}
          >
            <Image
              zIndex={1}
              objectFit="cover"
              width="100%"
              height="100%"
              aspectRatio="2 / 3"
              src={movie.poster_url as string}
              alt={`${movie.title} Poster`}
            />
          </Link>
          <Box
            marginBottom={2}
            marginTop={2}
            position="absolute"
            zIndex={0}
            left={2}
            top={0}
          >
            {color !== "hidden" && (
              <Icon as={HiMiniStar} boxSize={6} color={color} />
            )}
          </Box>
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
                onMovieUpdate={handleMovieUpdate}
                isHovered={isHovered}
              />
            </Box>
          )}
        </Box>
      </Card>
    </Box>
  );
};

export default MovieCard;
