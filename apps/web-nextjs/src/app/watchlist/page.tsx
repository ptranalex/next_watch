"use client";

import { Watchlist } from "@/src/components/user/watchlist";
import { Box, Container } from "@chakra-ui/react";

export default function WatchlistPage() {
  // In a real app, you would get the user ID from authentication
  // For now, using a mock user ID
  const userId = "user123";

  return (
    <Container maxW="container.xl" py={8}>
      <Box>
        <Watchlist userId={userId} />
      </Box>
    </Container>
  );
}
