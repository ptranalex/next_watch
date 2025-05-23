import { Box } from "@chakra-ui/react";
import React from "react";
import type { MovieCardContainerProps } from "./types";

const MovieCardContainer = ({ children }: MovieCardContainerProps) => {
  return (
    <Box
      _hover={{
        transform: "scale(1.03)",
        transition: "transform 0.1s ease-in-out",
      }}
      borderRadius={5}
      overflow="hidden"
      boxShadow="lg"
    >
      {children}
    </Box>
  );
};

export default MovieCardContainer;
