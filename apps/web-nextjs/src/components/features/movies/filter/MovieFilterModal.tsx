import MovieFilter from "./MovieFilter";
import useMovieFilterStore from "@/store/movieFilterStore";
import {
  Button,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Stack,
  Text,
  useToast,
} from "@chakra-ui/react";
import React from "react";
import { HiArrowPath, HiArrowRight } from "react-icons/hi2";
import { createLogger } from "@/utils/logging";
import type { MovieFilterModalProps } from "./types";

// Create logger for this component
const logger = createLogger("MovieFilterModal");

const MovieFilterModal: React.FC<MovieFilterModalProps> = ({
  isOpen,
  onClose,
}) => {
  const toast = useToast();
  const { resetFilters } = useMovieFilterStore();

  const onApply = () => {
    logger.info("Applying movie filters");
    toast({
      title: "Filters applied",
      status: "success",
      duration: 2000,
      isClosable: true,
    });
    onClose();
  };

  const onReset = () => {
    logger.info("Resetting movie filters");
    resetFilters();
    toast({
      title: "Filters reset",
      status: "info",
      duration: 2000,
      isClosable: true,
    });
    onClose();
  };

  return (
    <Modal isCentered isOpen={isOpen} onClose={onClose} size="xs">
      <ModalOverlay
        bg="blackAlpha.300"
        backdropFilter="auto"
        backdropBlur="4px"
      />
      <ModalContent bg="bg.secondary" color="text.primary" mx={2}>
        <ModalHeader>
          <Text fontSize="xl">Movie Filter</Text>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody padding={4}>
          <Stack spacing={4}>
            <MovieFilter />
            <Button
              bg="colors.primary"
              color="text.inverse"
              _hover={{ bg: "colors.primary.darker" }}
              leftIcon={<HiArrowRight />}
              onClick={onApply}
              width="100%"
              justifyContent="left"
            >
              Apply
            </Button>
            <Button
              variant="outline"
              leftIcon={<HiArrowPath />}
              onClick={onReset}
              width="100%"
              justifyContent="left"
              borderColor="text.tertiary"
              _hover={{ bg: "bg.tertiary" }}
            >
              Reset
            </Button>
          </Stack>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default MovieFilterModal;
