"use client";

import { Center, VStack, Heading, Text, Button } from "@chakra-ui/react";
import { createLogger } from "@/utils/logging";
import { useEffect } from "react";

// Create logger for error handling
const logger = createLogger("ErrorPage");

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  // Log error details when the component mounts
  useEffect(() => {
    // Log the error with all available details
    logger.error(`Application error occurred: ${error.message}`, {
      name: error.name,
      stack: error.stack,
      digest: error.digest,
    });
  }, [error]);

  // Log when user attempts to reset
  const handleReset = () => {
    logger.info("User triggered error reset");
    reset();
  };

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
          onClick={handleReset}
          size="lg"
        >
          Try again
        </Button>
      </VStack>
    </Center>
  );
}
