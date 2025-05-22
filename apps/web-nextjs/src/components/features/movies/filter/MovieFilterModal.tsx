import MovieFilter from "@/components/features/movies/filter/MovieFilter";
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
  useColorModeValue,
  useToast,
} from "@chakra-ui/react";
import React from "react";
import { HiArrowPath, HiArrowRight } from "react-icons/hi2";
import { createLogger } from "@/utils/logging";

// Create logger for this component
const logger = createLogger("MovieFilterModal");

interface MovieFilterModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const MovieFilterModal: React.FC<MovieFilterModalProps> = ({
  isOpen,
  onClose,
}) => {
  const textColor = useColorModeValue("black", "white");
  const modalBgColor = useColorModeValue("gray.100", "gray.800");
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
      <ModalContent bg={modalBgColor} color={textColor} mx={2}>
        <ModalHeader>
          <Text fontSize="xl">Movie Filter</Text>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody padding={4}>
          <Stack spacing={4}>
            <MovieFilter />
            <Button
              colorScheme="blue"
              leftIcon={<HiArrowRight />}
              onClick={onApply}
              width="100%"
              justifyContent="left"
            >
              Apply
            </Button>
            <Button
              colorScheme="gray"
              leftIcon={<HiArrowPath />}
              onClick={onReset}
              width="100%"
              justifyContent="left"
              variant="outline"
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
