import React from "react";
import { useDisclosure } from "@chakra-ui/react";
import { HiSortAscending } from "react-icons/hi";
import { createLogger } from "@/utils/logging";
import SortOptionsBottomSheet from "@/components/mobile/filters/SortOptionsBottomSheet";
import { FilterButtonAction } from "@/components/mobile/filters/FilterButton";

// Create logger for this component
const logger = createLogger("MobileSortButton");

/**
 * useMobileSortButton hook
 * Provides sort functionality and UI components for mobile interfaces
 * Returns both the action for BottomActionBar and the BottomSheet component
 */
export const useMobileSortButton = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const handleOpenSort = () => {
    logger.info("Opening mobile sort bottom sheet");
    onOpen();
  };

  const sortAction: FilterButtonAction = {
    icon: <HiSortAscending />,
    label: "Sort",
    onClick: handleOpenSort,
  };

  const sortBottomSheet = (
    <SortOptionsBottomSheet isOpen={isOpen} onClose={onClose} />
  );

  return { sortAction, sortBottomSheet };
};

export default useMobileSortButton;
