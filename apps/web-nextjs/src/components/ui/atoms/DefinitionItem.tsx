"use client";

import { Box, Heading } from "@chakra-ui/react";
import { ReactNode } from "react";

interface Props {
  term: string;
  children: ReactNode;
}

const DefinitionItem = ({ term, children }: Props) => {
  return (
    <Box marginY={5}>
      <Heading as="dt" fontSize="md" color="text.secondary">
        {term}
      </Heading>
      <Box as="dd" marginTop={2}>
        {children}
      </Box>
    </Box>
  );
};

export default DefinitionItem;
