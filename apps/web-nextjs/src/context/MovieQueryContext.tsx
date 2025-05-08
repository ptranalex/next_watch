"use client";

import { useRouter } from "next/navigation";
import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useState,
} from "react";

// Movie query interface that matches what was in the original Zustand store
interface MovieQuery {
  searchText: string;
  genre: string | null;
  sortOrder: string;
  sortDesc: boolean;
  rating_imdb: number | null;
  rating_rotten_tomatoes: number | null;
  rating_metacritic: number | null;
  year: number | null;
}

// Context interface
interface MovieQueryContextType {
  movieQuery: MovieQuery;
  setSearchText: (text: string) => void;
  setGenre: (genre: string | null) => void;
  setSortOrder: (order: string) => void;
  setSortDirection: (desc: boolean) => void;
  setSorting: (order: string, desc: boolean) => void;
  setRatingImdb: (rating: number | null) => void;
  setRatingTomatoes: (rating: number | null) => void;
  setRatingMetacritic: (rating: number | null) => void;
  setYear: (year: number | null) => void;
  reset: () => void;
}

// Default values
const defaultMovieQuery: MovieQuery = {
  searchText: "",
  genre: null,
  sortOrder: "release_date",
  sortDesc: true,
  rating_imdb: null,
  rating_rotten_tomatoes: null,
  rating_metacritic: null,
  year: null,
};

// Create the context
const MovieQueryContext = createContext<MovieQueryContextType>({
  movieQuery: defaultMovieQuery,
  setSearchText: () => {},
  setGenre: () => {},
  setSortOrder: () => {},
  setSortDirection: () => {},
  setSorting: () => {},
  setRatingImdb: () => {},
  setRatingTomatoes: () => {},
  setRatingMetacritic: () => {},
  setYear: () => {},
  reset: () => {},
});

// Hook to use the movie query context
export const useMovieQuery = () => useContext(MovieQueryContext);

// Movie Query Provider props
interface MovieQueryProviderProps {
  children: ReactNode;
}

// Movie Query Provider component
export const MovieQueryProvider = ({ children }: MovieQueryProviderProps) => {
  const router = useRouter();

  // State for movie query - now using default values directly
  const [movieQuery, setMovieQuery] = useState<MovieQuery>(defaultMovieQuery);

  // Setters for each property
  const setSearchText = useCallback((text: string) => {
    setMovieQuery((prev) => ({ ...prev, searchText: text }));
  }, []);

  const setGenre = useCallback((genre: string | null) => {
    setMovieQuery((prev) => ({ ...prev, genre }));
  }, []);

  const setSortOrder = useCallback((sortOrder: string) => {
    setMovieQuery((prev) => ({ ...prev, sortOrder }));
  }, []);

  const setSortDirection = useCallback((desc: boolean) => {
    setMovieQuery((prev) => ({ ...prev, sortDesc: desc }));
  }, []);

  const setSorting = useCallback((order: string, desc: boolean) => {
    setMovieQuery((prev) => ({ ...prev, sortOrder: order, sortDesc: desc }));
  }, []);

  const setRatingImdb = useCallback((rating: number | null) => {
    setMovieQuery((prev) => ({ ...prev, rating_imdb: rating }));
  }, []);

  const setRatingTomatoes = useCallback((rating: number | null) => {
    setMovieQuery((prev) => ({ ...prev, rating_rotten_tomatoes: rating }));
  }, []);

  const setRatingMetacritic = useCallback((rating: number | null) => {
    setMovieQuery((prev) => ({ ...prev, rating_metacritic: rating }));
  }, []);

  const setYear = useCallback((year: number | null) => {
    setMovieQuery((prev) => ({ ...prev, year }));
  }, []);

  const reset = useCallback(() => {
    setMovieQuery(defaultMovieQuery);
    router.push("/");
  }, [router]);

  return (
    <MovieQueryContext.Provider
      value={{
        movieQuery,
        setSearchText,
        setGenre,
        setSortOrder,
        setSortDirection,
        setSorting,
        setRatingImdb,
        setRatingTomatoes,
        setRatingMetacritic,
        setYear,
        reset,
      }}
    >
      {children}
    </MovieQueryContext.Provider>
  );
};

export default MovieQueryContext;
