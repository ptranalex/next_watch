import React from "react";
import { Box, Image, SimpleGrid, Text } from "@chakra-ui/react";
import Link from "next/link";
import { Actor } from "@/domain/entities";

interface ActorsGalleryProps {
  actors: Actor[];
}

const ActorsGallery: React.FC<ActorsGalleryProps> = ({ actors = [] }) => {
  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((word) => word[0])
      .join("");
  };

  if (!actors.length) {
    return null;
  }

  return (
    <Box>
      <SimpleGrid columns={3} spacing={2}>
        {actors.map((actor) => (
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
            <Link href={`/actors/${actor.id}`} key={actor.id}>
              {actor.profile_path ? (
                <Image src={actor.profile_path} alt={actor.name} />
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
