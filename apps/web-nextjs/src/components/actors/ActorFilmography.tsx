"use client";

import { useState, useEffect } from "react";
import {
  Box,
  VStack,
  Heading,
  Text,
  Image,
  HStack,
  Spinner,
  Link,
} from "@chakra-ui/react";
import NextLink from "next/link";
import { Movie } from "@/domain/entities";

interface FilmographyMovie {
  id: number;
  title: string;
  release_date: string;
  poster_path: string;
  character: string;
}

interface ActorFilmographyProps {
  actorId: string;
}

export default function ActorFilmography({ actorId }: ActorFilmographyProps) {
  const [movies, setMovies] = useState<FilmographyMovie[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchActorFilmography = async () => {
      setIsLoading(true);
      try {
        // Simulate API fetch - replace with actual API call
        await new Promise((resolve) => setTimeout(resolve, 1000));

        // Mock data for the actor's filmography
        const mockFilmography: FilmographyMovie[] = [
          {
            id: 1,
            title: "The Shawshank Redemption",
            release_date: "1994-09-23",
            poster_path: "https://via.placeholder.com/92x138?text=Shawshank",
            character: "Ellis Boyd 'Red' Redding",
          },
          {
            id: 2,
            title: "The Dark Knight",
            release_date: "2008-07-18",
            poster_path: "https://via.placeholder.com/92x138?text=DarkKnight",
            character: "Lucius Fox",
          },
          {
            id: 3,
            title: "Million Dollar Baby",
            release_date: "2004-12-15",
            poster_path:
              "https://via.placeholder.com/92x138?text=MillionDollar",
            character: "Eddie Scrap-Iron Dupris",
          },
          {
            id: 4,
            title: "Se7en",
            release_date: "1995-09-22",
            poster_path: "https://via.placeholder.com/92x138?text=Se7en",
            character: "Detective Lt. William Somerset",
          },
          {
            id: 5,
            title: "Bruce Almighty",
            release_date: "2003-05-23",
            poster_path: "https://via.placeholder.com/92x138?text=Bruce",
            character: "God",
          },
        ];

        setMovies(mockFilmography);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err : new Error("Unknown error occurred")
        );
      } finally {
        setIsLoading(false);
      }
    };

    fetchActorFilmography();
  }, [actorId]);

  if (isLoading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="md" />
      </Box>
    );
  }

  if (error) {
    return <Box>Error loading filmography: {error.message}</Box>;
  }

  if (!movies || movies.length === 0) {
    return <Box>No movie credits found for this actor.</Box>;
  }

  return (
    <Box border="1px" borderColor="gray.200" borderRadius="md" p={4}>
      <Heading as="h3" size="md" mb={4}>
        Filmography
      </Heading>

      <VStack spacing={4} align="stretch">
        {movies.map((movie) => (
          <Link
            as={NextLink}
            href={`/movies/${movie.id}`}
            key={String(movie.id)}
            _hover={{ textDecoration: "none" }}
          >
            <HStack
              spacing={3}
              p={2}
              borderRadius="md"
              _hover={{ bg: "gray.50", color: "blue.500" }}
              transition="all 0.2s"
            >
              <Image
                src={movie.poster_path}
                alt={movie.title}
                boxSize="50px"
                objectFit="cover"
                borderRadius="md"
                fallbackSrc="https://via.placeholder.com/50x75?text=No+Image"
              />
              <Box>
                <Text fontWeight="medium">{movie.title}</Text>
                <Text fontSize="sm" color="gray.600">
                  {new Date(movie.release_date).getFullYear()} •{" "}
                  {movie.character}
                </Text>
              </Box>
            </HStack>
          </Link>
        ))}
      </VStack>
    </Box>
  );
}
