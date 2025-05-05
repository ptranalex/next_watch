"use client";

import { FaImdb } from "react-icons/fa";
import { MdAssessment } from "react-icons/md";
import { SiRottentomatoes } from "react-icons/si";
import { HiCalendarDays } from "react-icons/hi2";
import { useMovieQuery } from "@/context/MovieQueryContext";
import RatingSlider from "./RatingSlider";

const MovieFilter = () => {
  // Use the context-based filter state which automatically updates the URL
  const {
    movieQuery: {
      rating_imdb,
      rating_rotten_tomatoes,
      rating_metacritic,
      year,
    },
    setRatingImdb,
    setRatingTomatoes,
    setRatingMetacritic,
    setYear,
  } = useMovieQuery();

  return (
    <>
      <RatingSlider
        key="imdb"
        step={0.5}
        max={10}
        min={0}
        value={rating_imdb ?? 0}
        setValue={setRatingImdb}
        icon={FaImdb}
      />
      <RatingSlider
        key="rotten_tomatoes"
        step={10}
        max={100}
        min={0}
        value={rating_rotten_tomatoes ?? 0}
        setValue={setRatingTomatoes}
        icon={SiRottentomatoes}
      />
      <RatingSlider
        key="metacritic"
        step={10}
        max={100}
        min={0}
        value={rating_metacritic ?? 0}
        setValue={setRatingMetacritic}
        icon={MdAssessment}
      />
      <RatingSlider
        key="year"
        step={1}
        max={2024}
        min={1990}
        value={year ?? 0}
        setValue={setYear}
        icon={HiCalendarDays}
      />
    </>
  );
};

export default MovieFilter;
