import { Box, Heading, Text } from "@chakra-ui/react";
import React from "react";

/**
 * Not found state for movie details
 */
const MovieNotFoundState: React.FC = () => {
  return (
    <Box textAlign="center" py={10}>
      <Heading size="md">Movie Not Found</Heading>
      <Text mt={4}>
        We couldn&apos;t find the movie you&apos;re looking for.
      </Text>
    </Box>
  );
};

export default React.memo(MovieNotFoundState);
