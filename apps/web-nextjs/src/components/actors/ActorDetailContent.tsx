"use client";

import { useState, useEffect } from "react";
import {
  Box,
  Image,
  VStack,
  Heading,
  Text,
  Spinner,
  Badge,
} from "@chakra-ui/react";
import DefinitionItem from "@/components/utils/DefinitionItem";
import { Actor } from "@/domain/entities";

interface ActorDetailContentProps {
  actorId: string;
}

export default function ActorDetailContent({
  actorId,
}: ActorDetailContentProps) {
  const [actor, setActor] = useState<Actor | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchActorDetails = async () => {
      setIsLoading(true);
      try {
        // Simulate API fetch - replace with actual API call
        await new Promise((resolve) => setTimeout(resolve, 800));

        // Mock data for the actor
        const mockActor: Actor = {
          id: parseInt(actorId),
          actor_id: parseInt(actorId),
          name: "Morgan Freeman",
          profile_path:
            "https://image.tmdb.org/t/p/w500/oIciQWr8VwKoR8TmAw1owaiZFyb.jpg",
          birth_date: "1937-06-01",
          place_of_birth: "Memphis, Tennessee, USA",
          biography:
            "Morgan Freeman is an American actor, film director, and narrator. Freeman has received Academy Award nominations for his performances in Street Smart, Driving Miss Daisy, The Shawshank Redemption and Invictus, and won the Best Supporting Actor Oscar in 2005 for Million Dollar Baby. He has also won a Golden Globe Award and a Screen Actors Guild Award.",
          gender: 2,
          popularity: 84.5,
        };

        setActor(mockActor);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err : new Error("Unknown error occurred")
        );
      } finally {
        setIsLoading(false);
      }
    };

    fetchActorDetails();
  }, [actorId]);

  if (isLoading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
      </Box>
    );
  }

  if (error) {
    return <Box>Error loading actor details: {error.message}</Box>;
  }

  if (!actor) {
    return <Box>No actor information available</Box>;
  }

  // Calculate age
  const calculateAge = () => {
    if (!actor.birth_date) return "Unknown";

    const birthDate = new Date(actor.birth_date);
    let endDate = new Date();

    if (actor.death_date) {
      endDate = new Date(actor.death_date);
    }

    let age = endDate.getFullYear() - birthDate.getFullYear();
    const monthDiff = endDate.getMonth() - birthDate.getMonth();

    if (
      monthDiff < 0 ||
      (monthDiff === 0 && endDate.getDate() < birthDate.getDate())
    ) {
      age--;
    }

    return age;
  };

  return (
    <Box>
      <VStack
        align="flex-start"
        spacing={6}
        mb={8}
        flexWrap={{ base: "wrap", md: "nowrap" }}
      >
        <Image
          src={actor.profile_path}
          alt={actor.name}
          borderRadius="md"
          maxW={{ base: "100%", md: "250px" }}
          fallbackSrc="https://via.placeholder.com/250x375?text=No+Image"
        />

        <VStack align="flex-start" spacing={4}>
          <Heading as="h2" size="xl">
            {actor.name}
          </Heading>

          <VStack align="flex-start" spacing={2} width="100%">
            <DefinitionItem term="Birthday">
              {actor.birth_date ? (
                <Text>
                  {new Date(actor.birth_date).toLocaleDateString()}
                  <Badge ml={2} colorScheme="blue">
                    {calculateAge()} years old
                  </Badge>
                </Text>
              ) : (
                "Unknown"
              )}
            </DefinitionItem>

            {actor.death_date && (
              <DefinitionItem term="Died">
                <Text>{new Date(actor.death_date).toLocaleDateString()}</Text>
              </DefinitionItem>
            )}

            <DefinitionItem term="Place of Birth">
              <Text>{actor.place_of_birth || "Unknown"}</Text>
            </DefinitionItem>

            <DefinitionItem term="Gender">
              <Text>
                {actor.gender === 1
                  ? "Female"
                  : actor.gender === 2
                  ? "Male"
                  : "Other"}
              </Text>
            </DefinitionItem>

            <DefinitionItem term="Popularity">
              <Text>{actor.popularity?.toFixed(1)}</Text>
            </DefinitionItem>
          </VStack>
        </VStack>
      </VStack>

      <Box mt={6}>
        <Heading as="h3" size="md" mb={3}>
          Biography
        </Heading>
        <Text>{actor.biography || "No biography available."}</Text>
      </Box>
    </Box>
  );
}
