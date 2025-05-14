"use client";

import { Heading, Text, Button, Center, VStack } from "@chakra-ui/react";
import Link from "next/link";

/**
 * Custom 404 page
 * The AppShell is already provided by the root layout, so we just need the content
 */
export default function NotFound() {
  return (
    <Center minH="70vh" width="100%">
      <VStack spacing={8} textAlign="center">
        <Heading as="h1" size="2xl">
          404 - Page Not Found
        </Heading>
        <Text fontSize="xl">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </Text>
        <Link href="/" passHref>
          <Button colorScheme="blue" size="lg">
            Return to Home
          </Button>
        </Link>
      </VStack>
    </Center>
  );
}
