"use client";

import { Suspense } from "react";
import {
  Box,
  Container,
  Heading,
  Spinner,
  Grid,
  GridItem,
} from "@chakra-ui/react";
import ActorDetailContent from "@/components/actors/ActorDetailContent";
import ActorFilmography from "@/components/actors/ActorFilmography";

interface ActorDetailPageProps {
  params: {
    id: string;
  };
}

export default function ActorDetailPage({ params }: ActorDetailPageProps) {
  const actorId = params.id;

  return (
    <Container maxW="container.xl" py={8}>
      <Heading as="h1" mb={6} size="xl">
        Actor Details
      </Heading>

      <Suspense
        fallback={
          <Box py={10} textAlign="center">
            <Spinner size="xl" />
          </Box>
        }
      >
        <Grid templateColumns={{ base: "1fr", lg: "2fr 1fr" }} gap={8}>
          <GridItem>
            <ActorDetailContent actorId={actorId} />
          </GridItem>

          <GridItem>
            <ActorFilmography actorId={actorId} />
          </GridItem>
        </Grid>
      </Suspense>
    </Container>
  );
}
