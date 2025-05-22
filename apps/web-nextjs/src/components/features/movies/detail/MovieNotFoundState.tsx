import { Box, Heading, Text } from "@chakra-ui/react";
import React from "react";

interface MovieNotFoundStateProps {
  message?: string;
}

/**
 * Not found state for movie details
 */
const MovieNotFoundState: React.FC<MovieNotFoundStateProps> = ({ message }) => {
  return (
    <Box textAlign="center" py={10}>
      <Heading size="md">Movie Not Found</Heading>
      <Text mt={4}>
        {message || "We couldn't find the movie you're looking for."}
      </Text>
    </Box>
  );
};

export default React.memo(MovieNotFoundState);
