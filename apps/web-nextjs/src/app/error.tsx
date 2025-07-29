"use client";

import React from "react";
import {
  Center,
  VStack,
  Heading,
  Text,
  Button,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from "@chakra-ui/react";
import { createLogger } from "@/utils/logging";
import { useEffect, useState } from "react";

// Create logger for error handling
const logger = createLogger("ErrorPage");

/**
 * Global error boundary for Next.js App Router
 *
 * Handles app-level errors according to industry standards:
 * - Network/connection errors (500+, DNS, offline)
 * - Unhandled JavaScript exceptions
 * - React rendering errors
 * - Third-party service failures
 */
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const [isOnline, setIsOnline] = useState(true);

  // Check if error is network-related
  const isNetworkError = React.useMemo(() => {
    const message = error.message.toLowerCase();
    return (
      message.includes("network") ||
      message.includes("fetch") ||
      message.includes("timeout") ||
      message.includes("connection") ||
      message.includes("offline") ||
      error.name === "NetworkError"
    );
  }, [error]);

  // Monitor online status for network errors
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    setIsOnline(navigator.onLine);
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  // Log error details when the component mounts
  useEffect(() => {
    logger.error(`Application error occurred: ${error.message}`, {
      name: error.name,
      stack: error.stack,
      digest: error.digest,
      isNetworkError,
      isOnline,
      userAgent: navigator.userAgent,
    });
  }, [error, isNetworkError, isOnline]);

  // Handle reset with different strategies based on error type
  const handleReset = () => {
    logger.info("User triggered error reset", {
      errorType: isNetworkError ? "network" : "application",
    });

    if (isNetworkError && !isOnline) {
      // For offline network errors, wait a moment then retry
      setTimeout(reset, 1000);
    } else {
      reset();
    }
  };

  // Network error UI (industry standard: prominent but not blocking)
  if (isNetworkError) {
    return (
      <Center minH="70vh" width="100%" px={4}>
        <VStack spacing={6} textAlign="center" maxW="md">
          <Alert
            status="warning"
            borderRadius="lg"
            flexDirection="column"
            py={6}
          >
            <AlertIcon boxSize="40px" mr={0} />
            <AlertTitle mt={4} mb={1} fontSize="lg">
              {!isOnline ? "You're Offline" : "Connection Problem"}
            </AlertTitle>
            <AlertDescription textAlign="center">
              {!isOnline
                ? "Check your internet connection and we'll automatically retry."
                : "We're having trouble connecting to our servers. This usually resolves quickly."}
            </AlertDescription>
          </Alert>

          <Button
            colorScheme="orange"
            onClick={handleReset}
            size="lg"
            isDisabled={!isOnline}
          >
            {!isOnline ? "Waiting for connection..." : "Retry"}
          </Button>

          <Text fontSize="sm" color="gray.500">
            Error: {error.message}
          </Text>
        </VStack>
      </Center>
    );
  }

  // Application error UI (critical errors requiring user action)
  return (
    <Center minH="70vh" width="100%" px={4}>
      <VStack spacing={8} textAlign="center" maxW="md">
        <Heading as="h1" size="2xl" color="red.500">
          Something went wrong
        </Heading>

        <VStack spacing={4}>
          <Text fontSize="lg">
            An unexpected error occurred in the application.
          </Text>

          {process.env.NODE_ENV === "development" && (
            <Alert status="error" borderRadius="md">
              <AlertIcon />
              <VStack align="start" spacing={1}>
                <AlertTitle fontSize="sm">Development Error:</AlertTitle>
                <AlertDescription fontSize="xs" fontFamily="mono">
                  {error.message}
                </AlertDescription>
              </VStack>
            </Alert>
          )}
        </VStack>

        <VStack spacing={3}>
          <Button colorScheme="red" onClick={handleReset} size="lg">
            Try again
          </Button>

          <Button
            variant="ghost"
            onClick={() => (window.location.href = "/")}
            size="sm"
          >
            Go to homepage
          </Button>
        </VStack>
      </VStack>
    </Center>
  );
}
