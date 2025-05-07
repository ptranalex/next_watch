"use client";

import MovieFilterModal from "@/components/home/MovieFilterModal";
import useMovieQueryStore from "@/store/movieQuery";
import {
  HStack,
  Heading,
  IconButton,
  useBreakpointValue,
} from "@chakra-ui/react";
import { useState } from "react";
import { HiAdjustmentsHorizontal } from "react-icons/hi2";

interface MovieHeadingProps {
  title?: string;
}

const MovieHeading = ({ title }: MovieHeadingProps) => {
  const movieQuery = useMovieQueryStore((state) => state.movieQuery);
  const showFilter = useBreakpointValue({ base: true, lg: false });

  const heading = `${movieQuery?.year || ""} ${
    movieQuery?.imdb_rating || ""
  } Movies`;

  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <HStack>
      <Heading
        as="h1"
        marginY={5}
        fontSize={{ base: "2xl", md: "3xl", lg: "4xl" }}
      >
        {title || heading}
      </Heading>
      {showFilter && (
        <>
          <IconButton
            aria-label="Login"
            icon={<HiAdjustmentsHorizontal />}
            onClick={handleOpenModal}
            fontSize={25}
          />
          <MovieFilterModal isOpen={isModalOpen} onClose={handleCloseModal} />
        </>
      )}
    </HStack>
  );
};

export default MovieHeading;
