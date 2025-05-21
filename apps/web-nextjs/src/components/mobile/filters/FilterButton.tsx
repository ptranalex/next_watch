import React from "react";
import { useDisclosure } from "@chakra-ui/react";
import { HiAdjustmentsHorizontal } from "react-icons/hi2";
import MovieFilterBottomSheet from "@/components/mobile/filters/MovieFilterBottomSheet";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("MobileFilterButton");

export interface FilterButtonAction {
  icon: React.ReactElement;
  label: string;
  onClick: () => void;
}

/**
 * useMobileFilterButton hook
 * Provides filter functionality and UI components for mobile interfaces
 * Returns both the action for BottomActionBar and the BottomSheet component
 */
export const useMobileFilterButton = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const handleOpenFilter = () => {
    logger.info("Opening mobile filter bottom sheet");
    onOpen();
  };

  const filterAction: FilterButtonAction = {
    icon: <HiAdjustmentsHorizontal />,
    label: "Filter",
    onClick: handleOpenFilter,
  };

  const filterBottomSheet = (
    <MovieFilterBottomSheet isOpen={isOpen} onClose={onClose} />
  );

  return { filterAction, filterBottomSheet };
};

export default useMobileFilterButton;
