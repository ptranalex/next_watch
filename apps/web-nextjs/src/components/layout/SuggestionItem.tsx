"use client";

// components/SuggestionItem.jsx
import { TextSuggestion } from "@/services/api/search/types";
import {
  Box,
  Link as ChakraLink,
  HStack,
  Icon,
  Image,
  Tag,
  Text,
} from "@chakra-ui/react";
import Link from "next/link";
import { HiFolder, HiOutlineFilm, HiTag, HiUserCircle } from "react-icons/hi2";

interface SuggestionItemProps {
  suggestion: TextSuggestion;
  onClick: () => void;
}

const SuggestionItem = ({ suggestion, onClick }: SuggestionItemProps) => {
  const getIcon = () => {
    switch (suggestion.type) {
      case "movie":
        return HiOutlineFilm;
      case "actor":
        return HiUserCircle;
      case "genre":
        return HiTag;
      default:
        return HiFolder;
    }
  };

  const getLink = () => {
    switch (suggestion.type) {
      case "movie":
        return `/movies/${suggestion.id}`;
      case "actor":
        return `/actors/${suggestion.id}`;
      case "genre":
        return `/genres/${suggestion.id}`;
      default:
        return "/";
    }
  };

  // Determine match quality indicator
  const getMatchIndicator = () => {
    switch (suggestion.search_type) {
      case "exact":
        return { color: "green.400", text: "Exact" };
      case "prefix":
        return { color: "blue.400", text: "Prefix" };
      case "word":
        return { color: "purple.400", text: "Word" };
      case "contains":
        return { color: "orange.400", text: "Contains" };
      default:
        return { color: "gray.400", text: "" };
    }
  };

  const matchIndicator = getMatchIndicator();

  // Get vote average rating display
  const getVoteAverage = () => {
    const voteAverage = suggestion.additional_info?.vote_average;
    if (!voteAverage) return null;

    let color = "gray.400";
    if (voteAverage >= 8.0) color = "***REMOVED***FFC107";
    else if (voteAverage >= 7.0) color = "***REMOVED***00E676";
    else if (voteAverage >= 6.0) color = "***REMOVED***82B1FF";

    return (
      <Text color={color} fontWeight="bold" fontSize="sm">
        {voteAverage.toFixed(1)}
      </Text>
    );
  };

  // Display formatted title if available
  const displayText =
    suggestion.additional_info?.original_title_format || suggestion.text;
  const yearText = suggestion.year ? ` (${suggestion.year})` : "";

  return (
    <ChakraLink
      as={Link}
      href={getLink()}
      onClick={onClick}
      textDecoration="none"
      _hover={{ textDecoration: "none" }}
      width="100%"
    >
      <HStack spacing={2} height="45px">
        {/* Image or icon */}
        {suggestion.image_path ? (
          <Image
            src={suggestion.image_path}
            alt={suggestion.text}
            width="30px"
            height="45px"
            objectFit="cover"
            borderRadius="sm"
          />
        ) : (
          <Box
            w="30px"
            h="45px"
            display="flex"
            alignItems="center"
            justifyContent="center"
          >
            <Icon as={getIcon()} w="20px" h="30px" />
          </Box>
        )}

        {/* Main suggestion text */}
        <Box flex="1">
          <Text
            fontWeight={suggestion.search_type === "exact" ? "bold" : "normal"}
          >
            {displayText}
            {yearText}
          </Text>

          {/* Additional details like type */}
          {suggestion.type && (
            <Text fontSize="xs" color="gray.400">
              {suggestion.type.charAt(0).toUpperCase() +
                suggestion.type.slice(1)}
            </Text>
          )}
        </Box>

        {/* Right side indicators */}
        <HStack spacing={1}>
          {/* Match quality indicator */}
          {matchIndicator.text && (
            <Tag
              size="sm"
              colorScheme={matchIndicator.color.split(".")[0]}
              variant="subtle"
            >
              {matchIndicator.text}
            </Tag>
          )}

          {/* Rating if available */}
          {getVoteAverage()}
        </HStack>
      </HStack>
    </ChakraLink>
  );
};

export default SuggestionItem;
