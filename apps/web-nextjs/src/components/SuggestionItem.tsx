import React from "react";
import { HStack, Icon, Image, Text, Box } from "@chakra-ui/react";
import Link from "next/link";
import { Movie, Genre } from "../services/movie-service";
import { BiMovie, BiFolder, BiUser } from "react-icons/bi";
import { Suggestion } from "../hooks/useSearchSuggestions";

interface SuggestionItemProps {
  item: Suggestion;
  onClick: () => void;
}

const SuggestionItem: React.FC<SuggestionItemProps> = ({ item, onClick }) => {
  if (item.type === "movie") {
    const movie = item.info as Movie;

    // Calculate rating color
    const getRatingColor = (rating?: number) => {
      if (!rating) return { color: "gray.400", star: "" };

      if (rating >= 8.0) return { color: "yellow.400", star: "★" };
      if (rating >= 7.0) return { color: "green.400", star: "★" };
      if (rating >= 6.0) return { color: "blue.400", star: "" };
      return { color: "gray.400", star: "" };
    };

    const { color, star } = getRatingColor(movie.vote_average);
    const releaseYear = movie.release_date
      ? new Date(movie.release_date).getFullYear()
      : "";

    return (
      <Link
        href={`/movies/${movie.id}`}
        passHref
        onClick={onClick}
        style={{ textDecoration: "none" }}
      >
        <HStack
          spacing={2}
          height="45px"
          p={2}
          borderRadius="md"
          _hover={{ bg: "gray.700" }}
        >
          {movie.poster_path ? (
            <Image
              src={`https://image.tmdb.org/t/p/w92${movie.poster_path}`}
              alt={movie.title}
              width="30px"
              fallbackSrc="/placeholder-poster.png"
            />
          ) : (
            <Icon as={BiMovie} boxSize="30px" />
          )}
          <Text>
            {movie.title} {releaseYear && `- ${releaseYear}`}
            {movie.vote_average && ` - ${movie.vote_average.toFixed(1)}`}
          </Text>
          <Text color={color}>{star}</Text>
        </HStack>
      </Link>
    );
  } else if (item.type === "actor") {
    const actor = item.info as any; // Using any temporarily until Actor type is fully defined

    return (
      <Link
        href={`/actors/${actor.id}`}
        passHref
        onClick={onClick}
        style={{ textDecoration: "none" }}
      >
        <HStack
          spacing={2}
          height="45px"
          p={2}
          borderRadius="md"
          _hover={{ bg: "gray.700" }}
        >
          {actor.profile_path ? (
            <Image
              src={`https://image.tmdb.org/t/p/w92${actor.profile_path}`}
              alt={actor.name}
              width="30px"
              fallbackSrc="/placeholder-person.png"
            />
          ) : (
            <Icon as={BiUser} boxSize="30px" />
          )}
          <Text>
            {actor.name}
            {actor.popularity && ` - ${actor.popularity.toFixed(1)}`}
          </Text>
        </HStack>
      </Link>
    );
  } else if (item.type === "genre") {
    const genre = item.info as Genre;

    return (
      <Link
        href={`/genre/${genre.name.toLowerCase()}`}
        passHref
        onClick={onClick}
        style={{ textDecoration: "none" }}
      >
        <HStack
          spacing={2}
          height="45px"
          p={2}
          borderRadius="md"
          _hover={{ bg: "gray.700" }}
        >
          <Icon as={BiFolder} boxSize="30px" />
          <Text>{genre.name}</Text>
        </HStack>
      </Link>
    );
  }

  return null;
};

export default SuggestionItem;
