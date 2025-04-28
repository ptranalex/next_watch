"use client";

import { useState } from "react";
import {
  Box,
  Text,
  AspectRatio,
  LinkBox,
  LinkOverlay,
  Heading,
  Badge,
  useColorModeValue,
  Image,
  Flex,
  IconButton,
} from "@chakra-ui/react";
import { HiPlay } from "react-icons/hi2";
import NextLink from "next/link";

interface TrailerCardProps {
  id: string;
  title: string;
  site: "YouTube" | "Vimeo";
  thumbnail?: string;
  publishedAt?: string;
  onClick?: () => void;
}

export default function TrailerCard({
  id,
  title,
  site,
  thumbnail,
  publishedAt,
  onClick,
}: TrailerCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const cardBg = useColorModeValue("white", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");

  // Format publish date if available
  const formattedDate = publishedAt
    ? new Date(publishedAt).toLocaleDateString()
    : null;

  // Generate the video URL based on the site and ID
  const getVideoUrl = () => {
    if (site === "YouTube") {
      return `https://www.youtube.com/watch?v=${id}`;
    } else if (site === "Vimeo") {
      return `https://vimeo.com/${id}`;
    }
    return "***REMOVED***";
  };

  // Generate the thumbnail URL
  const getThumbnailUrl = () => {
    if (thumbnail) {
      return thumbnail;
    }

    // Default YouTube thumbnail if no custom thumbnail provided
    if (site === "YouTube") {
      return `https://img.youtube.com/vi/${id}/hqdefault.jpg`;
    }

    // Fallback image
    return "https://via.placeholder.com/640x360?text=No+Thumbnail";
  };

  const handleCardClick = () => {
    if (onClick) {
      onClick();
    }

    // If not in an app that can handle the onClick (like opening a modal),
    // the user will navigate to the external link
  };

  return (
    <LinkBox
      borderWidth="1px"
      borderRadius="lg"
      overflow="hidden"
      bg={cardBg}
      borderColor={borderColor}
      transition="all 0.3s"
      _hover={{
        transform: "translateY(-4px)",
        shadow: "md",
        borderColor: "blue.500",
      }}
      onClick={handleCardClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <Box position="relative">
        <AspectRatio ratio={16 / 9}>
          <Image
            src={getThumbnailUrl()}
            alt={title}
            objectFit="cover"
            fallbackSrc="https://via.placeholder.com/640x360?text=Trailer"
          />
        </AspectRatio>

        {/* Play button overlay */}
        <Flex
          position="absolute"
          top="0"
          left="0"
          right="0"
          bottom="0"
          justify="center"
          align="center"
          bg={isHovered ? "blackAlpha.50" : "blackAlpha.0"}
          transition="all 0.3s"
        >
          <IconButton
            aria-label="Play trailer"
            icon={<HiPlay size="24px" />}
            size="lg"
            colorScheme="red"
            variant="solid"
            isRound
            opacity={isHovered ? 1 : 0.8}
            transform={isHovered ? "scale(1.1)" : "scale(1)"}
            transition="all 0.3s"
          />
        </Flex>

        {/* Site badge */}
        <Badge
          position="absolute"
          top={2}
          right={2}
          colorScheme={site === "YouTube" ? "red" : "blue"}
        >
          {site}
        </Badge>
      </Box>

      <Box p={4}>
        <LinkOverlay as={NextLink} href={getVideoUrl()} target="_blank">
          <Heading as="h3" size="sm" noOfLines={2} mb={1}>
            {title}
          </Heading>
        </LinkOverlay>

        {formattedDate && (
          <Text fontSize="sm" color="gray.500">
            Published: {formattedDate}
          </Text>
        )}
      </Box>
    </LinkBox>
  );
}
