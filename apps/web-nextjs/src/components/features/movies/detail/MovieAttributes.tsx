import { Genre } from "@/domain/entities";
import { Link as ChakraLink, SimpleGrid, Text, VStack } from "@chakra-ui/react";
import Link from "next/link";
import DefinitionItem from "@/components/ui/atoms/DefinitionItem";
import type { MovieAttributesProps } from "./types";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("MovieAttributes");

const MovieAttributes = ({ movie }: MovieAttributesProps) => {
  // Get cast directly from the movie object
  const cast = movie.cast || [];

  // Log movie and cast data on component render for debugging
  logger.debug("MovieAttributes data:", {
    id: movie.id,
    title: movie.title,
    hasCast: Array.isArray(cast) && cast.length > 0,
    castLength: cast.length,
  });

  // Helper to safely render movie properties
  const renderText = (value: unknown): string => {
    if (value === undefined || value === null) return "N/A";
    return String(value);
  };

  // Helper to safely render genres
  const renderGenres = () => {
    if (!movie.genres || !Array.isArray(movie.genres)) return "N/A";

    // Check if the array contains objects with a 'name' property
    return (
      movie.genres
        .filter(
          (genre): genre is Genre =>
            typeof genre === "object" && genre !== null && "name" in genre
        )
        .map((genre) => genre.name)
        .join(", ") || "N/A"
    );
  };

  // Helper to safely render cast
  const renderCast = () => {
    // Check if cast data exists
    if (!cast || cast.length === 0) {
      logger.warn("No cast data found", { movieId: movie.id });
      return <Text>N/A</Text>;
    }

    // Sort cast by order if available
    const sortedCast = [...cast].sort((a, b) =>
      a.order !== undefined && b.order !== undefined ? a.order - b.order : 0
    );

    // Limit to top 5 cast members to avoid cluttering the UI
    const displayCast = sortedCast.slice(0, 5);

    logger.debug("Rendering cast members:", { count: displayCast.length });

    return (
      <VStack align="flex-start" spacing={1}>
        {displayCast.map((actor) => (
          <ChakraLink
            as={Link}
            href={`/actors/${actor.id}`}
            key={actor.id}
            color="colors.primary"
            _hover={{ color: "colors.secondary" }}
          >
            <Text>
              {actor.name} {actor.character ? `as ${actor.character}` : ""}
            </Text>
          </ChakraLink>
        ))}
      </VStack>
    );
  };

  return (
    <SimpleGrid columns={2} as="dl">
      <DefinitionItem term="Genre">
        <Text>{renderGenres()}</Text>
      </DefinitionItem>
      <DefinitionItem term="Runtime">
        <Text>{renderText(movie.runtime)}</Text>
      </DefinitionItem>
      <DefinitionItem term="Cast">{renderCast()}</DefinitionItem>
      <DefinitionItem term="Director">
        <Text>{renderText(movie.director)}</Text>
      </DefinitionItem>
      <DefinitionItem term="Writer">
        <Text>{renderText(movie.writer)}</Text>
      </DefinitionItem>
      <DefinitionItem term="Awards">
        <Text>{renderText(movie.awards)}</Text>
      </DefinitionItem>
      <DefinitionItem term="Country (Language)">
        <Text>
          {renderText(movie.origin_country)} (
          {renderText(movie.original_language)})
        </Text>
      </DefinitionItem>
    </SimpleGrid>
  );
};

export default MovieAttributes;
