import React from "react";
import {
  VStack,
  Box,
  Heading,
  Text,
  Flex,
  Badge,
  HStack,
} from "@chakra-ui/react";
import { StarIcon, CalendarIcon } from "@chakra-ui/icons";
import Link from "next/link";

interface Genre {
  id: number;
  name: string;
}

interface MovieDetailsProps {
  title: string;
  overview: string;
  voteAverage?: number;
  releaseYear?: number | null;
  genres?: Genre[];
}

const MovieDetails: React.FC<MovieDetailsProps> = ({
  title,
  overview,
  voteAverage,
  releaseYear,
  genres,
}) => {
  return (
    <VStack align="start" spacing={4} width="100%">
      {/* Movie metadata */}
      <Flex wrap="wrap" gap={3} width="100%" justify="flex-start">
        {voteAverage !== undefined && (
          <Badge
            colorScheme={voteAverage > 7 ? "green" : "yellow"}
            px={2}
            py={1}
            display="flex"
            alignItems="center"
          >
            <StarIcon mr={1} boxSize={3} />
            {voteAverage.toFixed(1)}/10
          </Badge>
        )}

        {releaseYear && (
          <Badge
            px={2}
            py={1}
            colorScheme="blue"
            display="flex"
            alignItems="center"
          >
            <CalendarIcon mr={1} boxSize={3} />
            {releaseYear}
          </Badge>
        )}
      </Flex>

      {/* Genres */}
      {genres && genres.length > 0 && (
        <HStack spacing={2} wrap="wrap">
          {genres.map((genre) => (
            <Link
              href={`/genre/${genre.name.toLowerCase()}`}
              key={genre.id}
              passHref
            >
              <Badge
                colorScheme="blue"
                cursor="pointer"
                _hover={{ bg: "blue.500", color: "white" }}
              >
                {genre.name}
              </Badge>
            </Link>
          ))}
        </HStack>
      )}

      {/* Movie overview */}
      <Box>
        <Heading size="md" mb={2}>
          Overview
        </Heading>
        <Text>{overview || "No overview available."}</Text>
      </Box>
    </VStack>
  );
};

export default MovieDetails;
