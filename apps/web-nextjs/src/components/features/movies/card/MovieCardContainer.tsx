import { Box } from "@chakra-ui/react";
import React, { ReactNode } from "react";

interface Props {
  children: ReactNode;
}

const MovieCardContainer = ({ children }: Props) => {
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
