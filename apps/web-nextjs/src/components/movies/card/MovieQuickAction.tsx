"use client";

import {
  Box,
  HStack,
  IconButton,
  useDisclosure,
  useColorModeValue,
} from "@chakra-ui/react";
import { useState } from "react";
import { HiOutlineEllipsisVertical, HiLink } from "react-icons/hi2";
import CopyToClipBoardButton from "@/src/components/common/CopyToClipBoardButton";

interface MovieQuickActionProps {
  movieId: string;
  movieTitle: string;
}

export default function MovieQuickAction({
  movieId,
  movieTitle,
}: MovieQuickActionProps) {
  const { isOpen, onToggle, onClose } = useDisclosure();
  const [hovered, setHovered] = useState(false);

  const bgColor = useColorModeValue("white", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");

  // Construct movie URL
  const movieUrl = `${window.location.origin}/movies/${movieId}`;

  return (
    <Box
      position="absolute"
      top={2}
      right={2}
      zIndex={2}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => {
        setHovered(false);
        if (!isOpen) onClose();
      }}
    >
      {/* Main toggle button */}
      <IconButton
        aria-label="Movie actions"
        icon={<HiOutlineEllipsisVertical />}
        size="sm"
        borderRadius="full"
        onClick={onToggle}
        bg={isOpen || hovered ? bgColor : "transparent"}
        _hover={{ bg: bgColor }}
        visibility={isOpen || hovered ? "visible" : "hidden"}
        opacity={isOpen || hovered ? 1 : 0}
        transition="all 0.2s"
      />

      {/* Quick action menu */}
      {isOpen && (
        <Box
          position="absolute"
          top="100%"
          right={0}
          mt={1}
          borderRadius="md"
          boxShadow="md"
          bg={bgColor}
          borderWidth="1px"
          borderColor={borderColor}
          p={2}
          zIndex={3}
        >
          <HStack spacing={1}>
            {/* Copy link action */}
            <CopyToClipBoardButton
              textToCopy={movieUrl}
              tooltipText={`Copy link to ${movieTitle}`}
              successMessage="Link copied to clipboard!"
              aria-label="Copy movie link"
              icon={<HiLink />}
            />

            {/* Additional actions can be added here */}
          </HStack>
        </Box>
      )}
    </Box>
  );
}
