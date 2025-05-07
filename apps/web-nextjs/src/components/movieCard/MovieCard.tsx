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
import { useState } from "react";
import { HiMiniStar } from "react-icons/hi2";

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

  // This handler is called by the MovieQuickAction child component
  const handleMovieUpdate = async (updatedMovie: Movie) => {
    try {
      // First update local state for immediate UI feedback
      onMovieUpdate(updatedMovie);

      // Ensure movie.id is a number
      if (typeof movie.id !== "number") {
        throw new Error("Invalid movie ID");
      }

      // Then update the server state using the correct API endpoints
      if (updatedMovie.watched !== movie.watched) {
        await userInteractionAPI.toggleWatched(movie.id);
      }

      if (updatedMovie.liked !== movie.liked) {
        await userInteractionAPI.toggleLiked(movie.id);
      }

      if (updatedMovie.in_watchlist !== movie.in_watchlist) {
        await userInteractionAPI.toggleWatchlist(movie.id);
      }

      // Invalidate relevant queries to refetch data
      queryClient.invalidateQueries(["movie", movie.id]);
    } catch (error) {
      console.error("Failed to update movie interaction:", error);
      toast({
        title: "Update failed",
        description: "Failed to update movie status. Please try again.",
        status: "error",
        duration: 5000,
        isClosable: true,
      });

      // Revert the local state on error
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
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
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
