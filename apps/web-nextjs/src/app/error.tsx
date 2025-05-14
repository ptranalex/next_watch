"use client";

import { Center, VStack, Heading, Text, Button } from "@chakra-ui/react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <Center minH="70vh" width="100%">
      <VStack spacing={8} textAlign="center">
        <Heading
          as="h1"
          size="2xl"
          bgGradient="linear(to-r, red.400, red.600)"
          backgroundClip="text"
        >
          Something went wrong
        </Heading>
        <Text fontSize="xl">
          {error.message || "An unexpected error occurred."}
        </Text>
        <Button
          colorScheme="red"
          bgGradient="linear(to-r, red.400, red.500, red.600)"
          color="white"
          onClick={reset}
          size="lg"
        >
          Try again
        </Button>
      </VStack>
    </Center>
  );
}
