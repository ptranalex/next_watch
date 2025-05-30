import { getProfileUrl } from "@/utils/media";
import { Box, Grid, Image, Text, Tooltip } from "@chakra-ui/react";
import Link from "next/link";
import React, { useState } from "react";
import type { ActorGalleryProps, CastMember } from "../../actors/types";

const ActorsGallery: React.FC<ActorGalleryProps> = ({
  movieId,
  castData,
  maxActors = 6,
  showAllButton = false,
}) => {
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

  // Handle no cast data
  if (!castData?.cast?.length) {
    return null;
  }

  return (
    <Box width="100%">
      <Grid templateColumns="repeat(3, 1fr)" gap={2} width="100%">
        {castData.cast.slice(0, maxActors).map((actor: CastMember) => (
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
                    src={
                      getProfileUrl(actor.profile_path) ||
                      `https://image.tmdb.org/t/p/w300${actor.profile_path}`
                    }
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
                        backgroundColor="colors.primary"
                        borderRadius={4}
                      >
                        <Text
                          fontSize="2xl"
                          fontWeight="bold"
                          color="text.inverse"
                        >
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
                    backgroundColor="colors.primary"
                    borderRadius={4}
                  >
                    <Text fontSize="2xl" fontWeight="bold" color="text.inverse">
                      {getInitials(actor.name)}
                    </Text>
                  </Box>
                )}
              </Link>
            </Box>
          </Tooltip>
        ))}

        {/* Show "View All" button if there are more actors and showAllButton is true */}
        {showAllButton && castData.cast.length > maxActors && (
          <Box
            display="flex"
            alignItems="center"
            justifyContent="center"
            borderRadius={4}
            border="2px dashed"
            borderColor="colors.primary"
            _hover={{
              bg: "bg.tertiary",
              transform: "scale(1.05)",
              transition: "all 0.2s ease-in-out",
            }}
            position="relative"
            paddingBottom="150%"
            w="100%"
          >
            <Link
              href={`/movies/${movieId}/cast`}
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <Text fontSize="sm" color="colors.primary" textAlign="center">
                View All
                <br />({castData.cast.length})
              </Text>
            </Link>
          </Box>
        )}
      </Grid>
    </Box>
  );
};

export default ActorsGallery;
