"use client";

import RatingSlider from "@/components/home/RatingSlider";
import useMovieFilterStore from "@/store/movieFilterStore";
import { useCallback } from "react";
import { FaImdb } from "react-icons/fa";
import { HiCalendarDays } from "react-icons/hi2";
import { MdAssessment } from "react-icons/md";
import { SiRottentomatoes } from "react-icons/si";

// Define the filter param types
type FilterParams = Record<string, number | null> & {
  rating_imdb: number | null;
  rating_rotten_tomatoes: number | null;
  rating_metacritic: number | null;
  year: number | null;
};

const MovieFilter = () => {
  // Get store filters and actions
  const { filters, setFilter } = useMovieFilterStore();

  // Handlers for each rating type
  const handleImdbChange = useCallback(
    (value: number | null) => {
      setFilter("imdb_rating", value ?? undefined);
    },
    [setFilter]
  );

  const handleTomatoesChange = useCallback(
    (value: number | null) => {
      setFilter("rotten_tomatoes_rating", value ?? undefined);
    },
    [setFilter]
  );

  const handleMetacriticChange = useCallback(
    (value: number | null) => {
      setFilter("metacritic_rating", value ?? undefined);
    },
    [setFilter]
  );

  const handleYearChange = useCallback(
    (value: number | null) => {
      setFilter("year", value ?? undefined);
    },
    [setFilter]
  );

  return (
    <>
      <RatingSlider
        key="imdb"
        step={0.5}
        max={10}
        min={0}
        value={filters.imdb_rating}
        setValue={handleImdbChange}
        icon={FaImdb}
      />
      <RatingSlider
        key="rotten_tomatoes"
        step={10}
        max={100}
        min={0}
        value={filters.rotten_tomatoes_rating}
        setValue={handleTomatoesChange}
        icon={SiRottentomatoes}
      />
      <RatingSlider
        key="metacritic"
        step={10}
        max={100}
        min={0}
        value={filters.metacritic_rating}
        setValue={handleMetacriticChange}
        icon={MdAssessment}
      />
      <RatingSlider
        key="year"
        step={1}
        max={2024}
        min={1990}
        value={filters.year}
        setValue={handleYearChange}
        icon={HiCalendarDays}
      />
    </>
  );
};

export default MovieFilter;
