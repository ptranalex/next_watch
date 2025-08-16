"use client";

import { Box, HStack, Icon, Link as ChakraLink, Text } from "@chakra-ui/react";
import Link from "next/link";
import { IconType } from "react-icons";

interface SearchItemProps {
  /** The text to display in the search item */
  text: string;
  /** The icon to display on the left side */
  icon: IconType;
  /** The href URL for the link */
  href: string;
  /** Click handler function */
  onClick?: () => void;
  /** Optional additional props for accessibility */
  role?: string;
  "aria-selected"?: boolean;
}

const SearchItem = ({
  text,
  icon,
  href,
  onClick,
  role,
  "aria-selected": ariaSelected,
}: SearchItemProps) => {
  return (
    <ChakraLink
      as={Link}
      href={href}
      onClick={onClick}
      textDecoration="none"
      _hover={{ textDecoration: "none" }}
      width="100%"
      role={role}
      aria-selected={ariaSelected}
    >
      <HStack spacing={2} height="45px">
        {/* Icon container - matches SuggestionItem styling */}
        <Box
          w="30px"
          h="45px"
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <Icon as={icon} w="20px" h="30px" color="text.secondary" />
        </Box>

        {/* Main text - matches SuggestionItem styling */}
        <Box flex="1">
          <Text fontWeight="normal" color="text.primary">
            {text}
          </Text>
        </Box>
      </HStack>
    </ChakraLink>
  );
};

export default SearchItem;
