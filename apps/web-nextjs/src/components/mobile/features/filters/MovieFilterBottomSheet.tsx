import React, { useState } from "react";
import { Stack, Flex, useColorModeValue, useToast } from "@chakra-ui/react";
import { HiArrowPath, HiCheck } from "react-icons/hi2";
import MovieFilter from "@/components/features/movies/filter/MovieFilter";
import useMovieFilterStore from "@/store/movieFilterStore";
import { BottomSheet } from "@/components/mobile/ui/bottom-sheet";
import {
  MobilePrimaryCTA,
  MobileSecondaryCTA,
} from "@/components/mobile/ui/form";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("MovieFilterBottomSheet");

interface MovieFilterBottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
}

/**
 * MovieFilterBottomSheet component
 * A mobile-optimized filter interface using the BottomSheet pattern
 * Replaces the modal-based approach for a more touch-friendly experience
 */
const MovieFilterBottomSheet: React.FC<MovieFilterBottomSheetProps> = ({
  isOpen,
  onClose,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const textColor = useColorModeValue("black", "white");
  const toast = useToast();

  const { resetFilters } = useMovieFilterStore();

  const onApply = () => {
    logger.info("Applying movie filters");
    setIsLoading(true);

    // Simulate loading for better UX
    setTimeout(() => {
      toast({
        title: "Filters applied",
        status: "success",
        duration: 2000,
        isClosable: true,
        position: "bottom",
      });

      setIsLoading(false);
      onClose();
    }, 400);
  };

  const onReset = () => {
    logger.info("Resetting movie filters");
    setIsLoading(true);

    // Simulate loading for better UX
    setTimeout(() => {
      resetFilters();

      toast({
        title: "Filters reset",
        status: "info",
        duration: 2000,
        isClosable: true,
        position: "bottom",
      });

      setIsLoading(false);
      onClose();
    }, 400);
  };

  return (
    <BottomSheet
      isOpen={isOpen}
      onClose={onClose}
      title="Filter Movies"
      enableHaptics={true}
    >
      <Stack spacing={4} color={textColor} pt={4} pb={2}>
        <MovieFilter />
        <Flex direction="column" gap={3} mt="auto" pb={4}>
          <MobilePrimaryCTA
            icon={HiCheck}
            onClick={onApply}
            isLoading={isLoading}
            enableHaptics={true}
          >
            Apply Filters
          </MobilePrimaryCTA>
          <MobileSecondaryCTA
            icon={HiArrowPath}
            onClick={onReset}
            isLoading={isLoading}
            variant="outline"
            enableHaptics={true}
          >
            Reset All Filters
          </MobileSecondaryCTA>
        </Flex>
      </Stack>
    </BottomSheet>
  );
};

export default MovieFilterBottomSheet;
