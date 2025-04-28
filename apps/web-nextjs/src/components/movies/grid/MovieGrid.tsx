"use client";

import React, { useState, useEffect } from "react";
import { SimpleGrid, Box, Text } from "@chakra-ui/react";

interface Props {
  columns: {
    base: number;
    sm: number;
    md: number;
    lg: number;
  };
  source: string;
}

const MovieGrid: React.FC<Props> = ({ columns, source }) => {
  // This is a placeholder. In the real component, you would fetch movies based on source
  const movies = Array(12).fill(null); // Just for layout purposes

  console.log(`Fetching movies from source: ${source}`);

  return (
    <>
      {movies.length === 0 && (
        <Text>No movies found. Try adjusting your filters.</Text>
      )}

      <SimpleGrid columns={columns} spacing={6} padding={2}>
        {movies.map((_, index) => (
          <Box
            key={index}
            height="300px"
            borderRadius="lg"
            overflow="hidden"
            bg="gray.700"
          >
            {/* Placeholder for movie card */}
          </Box>
        ))}
      </SimpleGrid>
    </>
  );
};

export default MovieGrid;
