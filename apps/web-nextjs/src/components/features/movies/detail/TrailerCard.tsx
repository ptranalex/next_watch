import { useMovieTrailer } from "@/hooks";
import { Box, Spinner, Text, VStack } from "@chakra-ui/react";
import React from "react";
import type { TrailerCardProps } from "./types";

const TrailerCard: React.FC<TrailerCardProps> = ({ movieId }) => {
  // Call hook unconditionally first
  const { data: trailers, isLoading, error } = useMovieTrailer(movieId);

  // Handle invalid movie IDs
  if (!movieId || movieId <= 0) {
    return (
      <Box
        bg="bg.tertiary"
        height="300px"
        width="100%"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text color="text.tertiary">No trailer available</Text>
      </Box>
    );
  }

  if (isLoading) {
    return (
      <Box
        bg="bg.tertiary"
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
        bg="bg.tertiary"
        height="300px"
        width="100%"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text color="text.tertiary">Failed to load trailer</Text>
      </Box>
    );
  }

  if (!trailers || !Array.isArray(trailers) || trailers.length === 0) {
    return (
      <Box
        bg="bg.tertiary"
        height="300px"
        width="100%"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text color="text.tertiary">No trailer available</Text>
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
          bg="bg.tertiary"
          height="300px"
          width="100%"
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <Text color="text.tertiary">Invalid trailer data</Text>
        </Box>
      );
    }

    const trailerKey = trailer.youtube_key;
    // Add parameters to disable ads and improve performance/accessibility
    const trailerUrl = `https://www.youtube-nocookie.com/embed/${trailerKey}?modestbranding=1&rel=0&enablejsapi=0&cc_load_policy=1&iv_load_policy=3&fs=1&disablekb=0&controls=1&color=white&hl=en&playsinline=0&showinfo=0`;

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
            {/* Use iframe approach for both dev and production for better accessibility */}
            <iframe
              src={trailerUrl}
              width="100%"
              height="100%"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              title={trailer.name || "Movie Trailer"}
            />
          </Box>
        </Box>
        <Text fontSize="sm" color="text.tertiary">
          {trailer.name || "Movie Trailer"}
        </Text>
      </VStack>
    );
  } catch (err) {
    console.error("Error rendering trailer:", err);
    return (
      <Box
        bg="bg.tertiary"
        height="300px"
        width="100%"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text color="text.tertiary">Error displaying trailer</Text>
      </Box>
    );
  }
};

export default TrailerCard;
