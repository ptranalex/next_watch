import { Box, Spinner, Text } from "@chakra-ui/react";
import React from "react";

/**
 * Initial loading state for movie details (when ID is being resolved)
 */
const MovieInitialLoading: React.FC = () => {
  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      height="300px"
    >
      <Spinner size="xl" color="colors.primary" />
      <Text ml={4}>Loading movie details...</Text>
    </Box>
  );
};

export default React.memo(MovieInitialLoading);
