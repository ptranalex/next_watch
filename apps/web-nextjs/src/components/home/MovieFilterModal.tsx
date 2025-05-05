import { ViewIcon, ViewOffIcon } from "@chakra-ui/icons";
import {
  Button,
  FormControl,
  FormLabel,
  Input,
  InputGroup,
  InputRightElement,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Stack,
  Text,
  useColorModeValue,
} from "@chakra-ui/react";
import React, { useState } from "react";
import { HiArrowPath } from "react-icons/hi2";
import { HiArrowRight } from "react-icons/hi2";

import RatingSliderGroup from "./MovieFilter";
import useMovieQueryStore from "../../store/movieQuery";
import { on } from "events";

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

  const { resetFilters } = useMovieQueryStore();

  const onReset = () => {
    resetFilters();
    onClose();
  };

  return (
    <Modal isCentered isOpen={isOpen} onClose={onClose}>
      <ModalOverlay
        bg="blackAlpha.300"
        backdropFilter="auto"
        backdropBlur="4px"
      />
      <ModalContent bg={modalBgColor} color={textColor}>
        <ModalHeader>
          <Text fontSize="2xl">Movie Filter</Text>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody padding={6}>
          <Stack spacing={4}>
            <RatingSliderGroup />
            <Button
              colorScheme="blue"
              leftIcon={<HiArrowRight />}
              onClick={onClose}
              width="100%"
              justifyContent="left"
            >
              Apply
            </Button>
            <Button
              // colorScheme="red"
              leftIcon={<HiArrowPath />}
              onClick={onReset}
              width="100%"
              justifyContent="left"
              variant={"outline"}
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
