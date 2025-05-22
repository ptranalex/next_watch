import React from "react";
import { Button, Stack, useColorModeValue, useToast } from "@chakra-ui/react";
import { HiArrowPath, HiArrowRight } from "react-icons/hi2";
import MovieFilter from "@/components/features/movies/filter/MovieFilter";
import useMovieFilterStore from "@/store/movieFilterStore";
import BottomSheet from "@/components/mobile/common/BottomSheet";
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
  const textColor = useColorModeValue("black", "white");
  const toast = useToast();

  const { resetFilters } = useMovieFilterStore();

  const onApply = () => {
    logger.info("Applying movie filters");
    // Add haptic feedback
    if (window.navigator && "vibrate" in window.navigator) {
      try {
        window.navigator.vibrate(50);
      } catch (e) {
        logger.warn("Vibration not supported", e);
      }
    }

    toast({
      title: "Filters applied",
      status: "success",
      duration: 2000,
      isClosable: true,
      position: "bottom",
    });
    onClose();
  };

  const onReset = () => {
    logger.info("Resetting movie filters");
    resetFilters();

    // Add haptic feedback for reset
    if (window.navigator && "vibrate" in window.navigator) {
      try {
        window.navigator.vibrate([30, 50, 30]); // Pattern for reset
      } catch (e) {
        logger.warn("Vibration not supported", e);
      }
    }

    toast({
      title: "Filters reset",
      status: "info",
      duration: 2000,
      isClosable: true,
      position: "bottom",
    });
    onClose();
  };

  return (
    <BottomSheet isOpen={isOpen} onClose={onClose} height="60vh">
      <Stack spacing={5} color={textColor}>
        <MovieFilter />
        <Button
          colorScheme="blue"
          leftIcon={<HiArrowRight />}
          onClick={onApply}
          width="100%"
          justifyContent="left"
          size="lg"
          height="56px"
          borderRadius="md"
        >
          Apply Filters
        </Button>
        <Button
          colorScheme="gray"
          leftIcon={<HiArrowPath />}
          onClick={onReset}
          width="100%"
          justifyContent="left"
          variant="outline"
          size="lg"
          height="56px"
          borderRadius="md"
        >
          Reset All Filters
        </Button>
      </Stack>
    </BottomSheet>
  );
};

export default MovieFilterBottomSheet;
