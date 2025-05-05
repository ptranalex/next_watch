import {
  SimpleGrid,
  Text,
  Link as ChakraLink,
  Spinner,
} from "@chakra-ui/react";
import Link from "next/link";
import DefinitionItem from "../utils/DefinitionItem";
import { Movie, Genre } from "@/domain/entities";
import { useMovieCast } from "@/hooks";

interface Props {
  movie: Movie;
}

const MovieAttributes = ({ movie }: Props) => {
  // Use optional chaining and nullish coalescing to safely access movie.id
  const movieId = typeof movie.id === "number" ? movie.id : 0;
  const { data: castData, isLoading } = useMovieCast(movieId);

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

  return (
    <SimpleGrid columns={2} as="dl">
      <DefinitionItem term="Genre">
        <Text>{renderGenres()}</Text>
      </DefinitionItem>
      <DefinitionItem term="Runtime">
        <Text>{renderText(movie.runtime)}</Text>
      </DefinitionItem>
      <DefinitionItem term="Cast">
        {isLoading ? (
          <Spinner size="sm" />
        ) : (
          castData?.cast.slice(0, 3).map((actor) => (
            <ChakraLink
              as={Link}
              href={`/actors/${actor.actor_id}`}
              key={actor.id}
            >
              <Text>{actor.name}</Text>
            </ChakraLink>
          ))
        )}
      </DefinitionItem>
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
