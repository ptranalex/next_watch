import { useMovieCast } from "@/hooks/domain/movie/useMovieCast";
import { Box, Image, SimpleGrid, Spinner, Text } from "@chakra-ui/react";
import Link from "next/link";
import React, { useState } from "react";

// TMDB image base URL - use w300 for better quality
const TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w300";

interface ActorsGalleryProps {
  movieId: number;
}

const ActorsGallery: React.FC<ActorsGalleryProps> = ({ movieId }) => {
  // Fetch cast data using React Query
  const { data: castData, isLoading, error } = useMovieCast(movieId);

  // Keep track of images that failed to load
  const [failedImages, setFailedImages] = useState<Record<number, boolean>>({});

  // Get initials when no profile image is available
  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((word) => word?.[0] || "")
      .join("")
      .substring(0, 2);
  };

  // Handle image loading error
  const handleImageError = (actorId: number) => {
    setFailedImages((prev) => ({
      ...prev,
      [actorId]: true,
    }));
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

  return (
    <Box>
      <SimpleGrid columns={3} spacing={2}>
        {castData.cast.map((actor) => (
          <Box
            key={actor.id}
            textAlign="center"
            _hover={{
              transform: "scale(1.05)",
              transition: "transform 0.2s ease-in-out",
            }}
            borderRadius={4}
            overflow="hidden"
            height="160px"
          >
            <Link
              href={`/actors/${actor.actor_id}`}
              style={{ display: "block", height: "100%" }}
            >
              {actor.profile_path && !failedImages[actor.id] ? (
                <Image
                  src={`${TMDB_IMAGE_BASE}${actor.profile_path}`}
                  alt={actor.name}
                  width="100%"
                  height="100%"
                  objectFit="cover"
                  onError={() => handleImageError(actor.id)}
                  fallback={
                    <Box
                      width="100%"
                      height="100%"
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                      backgroundColor="blue.700"
                    >
                      <Text fontSize="2xl" fontWeight="bold" color="white">
                        {getInitials(actor.name)}
                      </Text>
                    </Box>
                  }
                />
              ) : (
                <Box
                  width="100%"
                  height="100%"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                  backgroundColor="blue.700"
                >
                  <Text fontSize="2xl" fontWeight="bold" color="white">
                    {getInitials(actor.name)}
                  </Text>
                </Box>
              )}
              <Text
                fontSize="sm"
                mt={1}
                noOfLines={1}
                textAlign="center"
                fontWeight="medium"
              >
                {actor.name}
              </Text>
            </Link>
          </Box>
        ))}
      </SimpleGrid>
    </Box>
  );
};

export default ActorsGallery;
