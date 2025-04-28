import { Box, Heading, Text } from "@chakra-ui/react";
import { ReactNode } from "react";

interface DefinitionItemProps {
  term: string;
  children: ReactNode;
}

export default function DefinitionItem({
  term,
  children,
}: DefinitionItemProps) {
  return (
    <Box>
      <Heading as="h4" size="xs" color="gray.500" fontWeight="medium">
        {term}
      </Heading>
      <Text mt={1}>{children}</Text>
    </Box>
  );
}
