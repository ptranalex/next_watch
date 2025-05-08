import { Box, Container, Heading, Text, Button } from "@chakra-ui/react";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default function NotFound() {
  return (
    <Container maxW="container.xl" py={20}>
      <Box textAlign="center">
        <Heading as="h1" size="2xl" mb={4}>
          404 - Page Not Found
        </Heading>
        <Text fontSize="xl" mb={8}>
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </Text>
        <Link href="/" passHref>
          <Button colorScheme="blue" size="lg">
            Return to Home
          </Button>
        </Link>
      </Box>
    </Container>
  );
}
