import { Box, Heading, Text } from "@chakra-ui/react";
import React from "react";
import type { MovieErrorStateProps } from "./types";

/**
 * Error state display for movie details
 */
const MovieErrorState: React.FC<MovieErrorStateProps> = ({ error }) => {
  // Log error for debugging
  if (error) {
    console.error("Error loading movie:", error);
  }

  return (
    <Box textAlign="center" py={10}>
      <Heading size="md">Error Loading Movie</Heading>
      <Text mt={4}>
        Sorry, we couldn&apos;t load this movie. Please try again later.
      </Text>
    </Box>
  );
};

export default React.memo(MovieErrorState);
