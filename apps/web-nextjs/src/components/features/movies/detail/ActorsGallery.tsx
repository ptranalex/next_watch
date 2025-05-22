import { useMovieCast } from "@/hooks/domain/movie/useMovieCast";
import { Box, Image, Grid, Spinner, Text, Tooltip } from "@chakra-ui/react";
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
    <Box width="100%">
      <Grid templateColumns="repeat(3, 1fr)" gap={2} width="100%">
        {castData.cast.slice(0, 6).map((actor) => (
          <Tooltip
            key={actor.id}
            label={actor.name}
            aria-label={`Actor: ${actor.name}`}
            placement="top"
            hasArrow
            openDelay={300}
          >
            <Box
              textAlign="center"
              _hover={{
                transform: "scale(1.05)",
                transition: "transform 0.2s ease-in-out",
              }}
              borderRadius={4}
              overflow="hidden"
              position="relative"
              paddingBottom="150%" // 2:3 aspect ratio (height is 150% of width)
              w="100%"
            >
              <Link
                href={`/actors/${actor.actor_id}`}
                style={{
                  position: "absolute",
                  top: 0,
                  left: 0,
                  width: "100%",
                  height: "100%",
                }}
              >
                {actor.profile_path && !failedImages[actor.id] ? (
                  <Image
                    src={`${TMDB_IMAGE_BASE}${actor.profile_path}`}
                    alt={actor.name}
                    position="absolute"
                    top={0}
                    left={0}
                    width="100%"
                    height="100%"
                    objectFit="cover"
                    borderRadius={4}
                    onError={() => handleImageError(actor.id)}
                    fallback={
                      <Box
                        position="absolute"
                        top={0}
                        left={0}
                        width="100%"
                        height="100%"
                        display="flex"
                        alignItems="center"
                        justifyContent="center"
                        backgroundColor="blue.700"
                        borderRadius={4}
                      >
                        <Text fontSize="2xl" fontWeight="bold" color="white">
                          {getInitials(actor.name)}
                        </Text>
                      </Box>
                    }
                  />
                ) : (
                  <Box
                    position="absolute"
                    top={0}
                    left={0}
                    width="100%"
                    height="100%"
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    backgroundColor="blue.700"
                    borderRadius={4}
                  >
                    <Text fontSize="2xl" fontWeight="bold" color="white">
                      {getInitials(actor.name)}
                    </Text>
                  </Box>
                )}
              </Link>
            </Box>
          </Tooltip>
        ))}
      </Grid>
    </Box>
  );
};

export default ActorsGallery;
