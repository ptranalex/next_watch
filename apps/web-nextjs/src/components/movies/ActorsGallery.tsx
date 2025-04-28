"use client";

import {
  Box,
  SimpleGrid,
  Text,
  Image,
  Heading,
  LinkBox,
  LinkOverlay,
  useColorModeValue,
  VStack,
} from "@chakra-ui/react";
import NextLink from "next/link";

interface Actor {
  id: string;
  name: string;
  character?: string;
  profile_path?: string;
}

interface ActorsGalleryProps {
  actors: Actor[];
  title?: string;
  maxDisplay?: number;
}

export default function ActorsGallery({
  actors,
  title = "Cast",
  maxDisplay = 6,
}: ActorsGalleryProps) {
  const cardBg = useColorModeValue("white", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");

  if (!actors || actors.length === 0) {
    return null;
  }

  // Limit the number of actors to display
  const displayActors = actors.slice(0, maxDisplay);

  return (
    <Box my={6}>
      {title && (
        <Heading as="h3" size="md" mb={4}>
          {title}
        </Heading>
      )}

      <SimpleGrid columns={{ base: 2, sm: 3, md: 4, lg: 6 }} spacing={4}>
        {displayActors.map((actor) => (
          <LinkBox
            key={actor.id}
            borderWidth="1px"
            borderRadius="lg"
            overflow="hidden"
            bg={cardBg}
            borderColor={borderColor}
            transition="all 0.2s"
            _hover={{
              transform: "translateY(-4px)",
              shadow: "md",
              borderColor: "blue.400",
            }}
          >
            <Image
              src={
                actor.profile_path ||
                `https://via.placeholder.com/150x225?text=${encodeURIComponent(
                  actor.name
                )}`
              }
              alt={actor.name}
              width="100%"
              height="180px"
              objectFit="cover"
              fallbackSrc={`https://via.placeholder.com/150x225?text=${encodeURIComponent(
                actor.name
              )}`}
            />
            <VStack p={3} align="start" spacing={0}>
              <LinkOverlay
                as={NextLink}
                href={`/actors/${actor.id}`}
                fontWeight="medium"
                noOfLines={1}
              >
                {actor.name}
              </LinkOverlay>
              {actor.character && (
                <Text fontSize="sm" color="gray.500" noOfLines={1}>
                  {actor.character}
                </Text>
              )}
            </VStack>
          </LinkBox>
        ))}
      </SimpleGrid>

      {actors.length > maxDisplay && (
        <Box textAlign="center" mt={4}>
          <NextLink href="***REMOVED***" passHref>
            <Text color="blue.500" fontWeight="medium">
              View all {actors.length} cast members
            </Text>
          </NextLink>
        </Box>
      )}
    </Box>
  );
}
