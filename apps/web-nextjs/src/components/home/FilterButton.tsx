"use client";

import MovieFilterModal from "@/components/home/MovieFilterModal";
import {
  IconButton,
  useDisclosure,
  useBreakpointValue,
} from "@chakra-ui/react";
import React from "react";
import { HiAdjustmentsHorizontal } from "react-icons/hi2";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("FilterButton");

/**
 * FilterButton component
 * Renders a filter icon button that opens the MovieFilterModal when clicked
 * Only displays on mobile devices
 */
const FilterButton: React.FC = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const isMobile = useBreakpointValue({ base: true, md: false });

  const handleOpenFilter = () => {
    logger.info("Opening filter modal");
    onOpen();
  };

  // Only render on mobile
  if (!isMobile) return null;

  return (
    <>
      <IconButton
        aria-label="Filter movies"
        icon={<HiAdjustmentsHorizontal />}
        onClick={handleOpenFilter}
        variant="solid"
        fontSize="22px"
        ml={5}
      />
      <MovieFilterModal isOpen={isOpen} onClose={onClose} />
    </>
  );
};

export default FilterButton;
