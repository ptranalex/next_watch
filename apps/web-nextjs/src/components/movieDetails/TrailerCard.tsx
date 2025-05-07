import { useMovieTrailer } from "@/hooks";
import { Box, Spinner, Text, VStack } from "@chakra-ui/react";
import React from "react";
import ReactPlayer from "react-player/youtube";

interface TrailerCardProps {
  movieId: number;
}

const TrailerCard: React.FC<TrailerCardProps> = ({ movieId }) => {
  // Handle invalid movie IDs
  if (!movieId || movieId <= 0) {
    return (
      <Box
        bg="gray.700"
        height="300px"
        width="100%"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text color="gray.400">No trailer available</Text>
      </Box>
    );
  }

  const { data: trailers, isLoading, error } = useMovieTrailer(movieId);

  if (isLoading) {
    return (
      <Box
        bg="gray.700"
        height="300px"
        width="100%"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Spinner />
      </Box>
    );
  }

  if (error) {
    console.error("Error loading trailer:", error);
    return (
      <Box
        bg="gray.700"
        height="300px"
        width="100%"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text color="gray.400">Failed to load trailer</Text>
      </Box>
    );
  }

  if (!trailers || !Array.isArray(trailers) || trailers.length === 0) {
    return (
      <Box
        bg="gray.700"
        height="300px"
        width="100%"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text color="gray.400">No trailer available</Text>
      </Box>
    );
  }

  // Get the first official trailer, or fall back to the first trailer
  try {
    const trailer =
      trailers.find((t) => t && typeof t === "object" && t.is_official) ||
      trailers[0];

    // Check if trailer is valid and has the required properties
    if (!trailer || typeof trailer !== "object" || !trailer.youtube_key) {
      return (
        <Box
          bg="gray.700"
          height="300px"
          width="100%"
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <Text color="gray.400">Invalid trailer data</Text>
        </Box>
      );
    }

    const trailerUrl = `https://www.youtube.com/watch?v=${trailer.youtube_key}`;

    return (
      <VStack spacing={2} align="stretch">
        <Box
          position="relative"
          paddingTop="56.25%" /* 16:9 Aspect Ratio */
          width="100%"
        >
          <Box
            position="absolute"
            top="0"
            left="0"
            width="100%"
            height="100%"
            maxHeight={360}
          >
            <ReactPlayer
              url={trailerUrl}
              width="100%"
              height="100%"
              controls={true}
              playing={false}
            />
          </Box>
        </Box>
        <Text fontSize="sm" color="gray.500">
          {trailer.name || "Movie Trailer"}
        </Text>
      </VStack>
    );
  } catch (err) {
    console.error("Error rendering trailer:", err);
    return (
      <Box
        bg="gray.700"
        height="300px"
        width="100%"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text color="gray.400">Error displaying trailer</Text>
      </Box>
    );
  }
};

export default TrailerCard;
