import React from "react";
import { Box, Image, SimpleGrid, Text, Spinner } from "@chakra-ui/react";
import Link from "next/link";
import { useMovieCast } from "@/hooks/domain/movie/useMovieCast";

// TMDB image base URL
const TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w200";

interface ActorsGalleryProps {
  movieId: number;
}

const ActorsGallery: React.FC<ActorsGalleryProps> = ({ movieId }) => {
  // Fetch cast data using React Query
  const { data: castData, isLoading, error } = useMovieCast(movieId);

  // Get initials when no profile image is available
  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((word) => word[0])
      .join("");
  };

  // Handle loading state
  if (isLoading) {
    return (
      <Box textAlign="center" py={2}>
        <Spinner size="sm" color="blue.500" mr={2} />
        <Text display="inline" fontSize="sm">
          Loading cast...
        </Text>
      </Box>
    );
  }

  // Handle error state
  if (error) {
    return (
      <Text fontSize="sm" color="gray.500">
        Unable to load cast
      </Text>
    );
  }

  // Handle no cast data
  if (!castData?.cast?.length) {
    return null;
  }

  // Get only top 3 actors
  const topActors = castData.cast.slice(0, 3);

  return (
    <Box>
      <SimpleGrid columns={3} spacing={2}>
        {topActors.map((actor) => (
          <Box
            key={actor.id}
            textAlign="center"
            _hover={{
              transform: "scale(1.05)",
              transition: "transform 0.2s ease-in-out",
            }}
            borderRadius={0}
            overflow="hidden"
          >
            <Link href={`/actors/${actor.actor_id}`}>
              {actor.profile_path ? (
                <Image
                  src={`${TMDB_IMAGE_BASE}${actor.profile_path}`}
                  alt={actor.name}
                  width="100%"
                  height="auto"
                />
              ) : (
                <Box
                  width="100%"
                  height="100%"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  backgroundColor="blue.300"
                >
                  <Text fontSize="2xl" fontWeight="bold" color="gray.700">
                    {getInitials(actor.name)}
                  </Text>
                </Box>
              )}
            </Link>
          </Box>
        ))}
      </SimpleGrid>
    </Box>
  );
};

export default ActorsGallery;
