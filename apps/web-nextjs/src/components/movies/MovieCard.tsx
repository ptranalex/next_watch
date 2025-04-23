import React from "react";
import {
  Box,
  Image,
  Heading,
  Text,
  Badge,
  Flex,
  useColorModeValue,
} from "@chakra-ui/react";
import { StarIcon } from "@chakra-ui/icons";
import Link from "next/link";
import { Movie } from "../../services/movie-service";

interface MovieCardProps {
  movie: Movie;
  size?: "sm" | "md" | "lg";
}

const MovieCard: React.FC<MovieCardProps> = ({ movie, size = "md" }) => {
  const cardBg = useColorModeValue("white", "gray.800");
  const textColor = useColorModeValue("gray.800", "white");

  // Set dimensions based on size
  const dimensions = {
    sm: { width: "150px", height: "225px", fontSize: "sm" },
    md: { width: "200px", height: "300px", fontSize: "md" },
    lg: { width: "250px", height: "375px", fontSize: "lg" },
  }[size];

  // Format release date if available
  const releaseYear = movie.release_date
    ? new Date(movie.release_date).getFullYear()
    : null;

  return (
    <Link href={`/movies/${movie.id}`} passHref>
      <Box
        width={dimensions.width}
        borderRadius="lg"
        overflow="hidden"
        bg={cardBg}
        boxShadow="md"
        transition="all 0.3s"
        _hover={{ transform: "translateY(-5px)", boxShadow: "lg" }}
        cursor="pointer"
      >
        <Image
          src={
            movie.poster_path
              ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
              : "/placeholder-poster.png"
          }
          alt={movie.title}
          width={dimensions.width}
          height={dimensions.height}
          objectFit="cover"
          fallbackSrc="/placeholder-poster.png"
        />

        <Box p={3}>
          <Heading
            as="h3"
            size={size === "sm" ? "xs" : "sm"}
            noOfLines={1}
            color={textColor}
            mb={1}
          >
            {movie.title}
          </Heading>

          <Flex justify="space-between" align="center">
            {releaseYear && (
              <Text fontSize="xs" color="gray.500">
                {releaseYear}
              </Text>
            )}

            {movie.vote_average !== undefined && (
              <Flex align="center">
                <StarIcon color="yellow.400" mr={1} boxSize={3} />
                <Text fontSize="xs" fontWeight="bold">
                  {movie.vote_average.toFixed(1)}
                </Text>
              </Flex>
            )}
          </Flex>

          {movie.genres && movie.genres.length > 0 && (
            <Flex mt={2} flexWrap="wrap" gap={1}>
              {movie.genres.slice(0, 2).map((genre) => (
                <Badge
                  key={genre.id}
                  colorScheme="blue"
                  fontSize="xx-small"
                  variant="subtle"
                >
                  {genre.name}
                </Badge>
              ))}
            </Flex>
          )}
        </Box>
      </Box>
    </Link>
  );
};

export default MovieCard;
