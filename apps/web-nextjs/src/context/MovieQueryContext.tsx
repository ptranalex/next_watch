"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
  useEffect,
} from "react";
import { useRouter, useSearchParams } from "next/navigation";

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
  const searchParams = useSearchParams();

  // Get query params from URL or use defaults
  const getQueryFromUrl = useCallback(() => {
    return {
      searchText: searchParams.get("search") || "",
      genre: searchParams.get("genre"),
      sortOrder: searchParams.get("sort") || "release_date",
      sortDesc: searchParams.get("desc") !== "false",
      rating_imdb: searchParams.get("imdb")
        ? Number(searchParams.get("imdb"))
        : null,
      rating_rotten_tomatoes: searchParams.get("rt")
        ? Number(searchParams.get("rt"))
        : null,
      rating_metacritic: searchParams.get("mc")
        ? Number(searchParams.get("mc"))
        : null,
      year: searchParams.get("year") ? Number(searchParams.get("year")) : null,
    };
  }, [searchParams]);

  // State for movie query
  const [movieQuery, setMovieQuery] = useState<MovieQuery>(getQueryFromUrl());

  // Update URL when movie query changes
  const updateUrl = useCallback(
    (newQuery: MovieQuery) => {
      const params = new URLSearchParams();

      if (newQuery.searchText) params.set("search", newQuery.searchText);
      if (newQuery.genre) params.set("genre", newQuery.genre);
      if (newQuery.sortOrder) params.set("sort", newQuery.sortOrder);
      params.set("desc", newQuery.sortDesc ? "true" : "false");
      if (newQuery.rating_imdb !== null)
        params.set("imdb", newQuery.rating_imdb.toString());
      if (newQuery.rating_rotten_tomatoes !== null)
        params.set("rt", newQuery.rating_rotten_tomatoes.toString());
      if (newQuery.rating_metacritic !== null)
        params.set("mc", newQuery.rating_metacritic.toString());
      if (newQuery.year !== null) params.set("year", newQuery.year.toString());

      // Log the params being set
      console.log("Updating URL with params:", params.toString(), newQuery);

      // Update URL without reloading the page
      router.push(`?${params.toString()}`);
    },
    [router]
  );

  // Update local state from URL whenever URL changes
  useEffect(() => {
    setMovieQuery(getQueryFromUrl());
  }, [searchParams, getQueryFromUrl]);

  // Setters for each property
  const setSearchText = useCallback(
    (text: string) => {
      const newQuery = { ...movieQuery, searchText: text };
      setMovieQuery(newQuery);
      updateUrl(newQuery);
    },
    [movieQuery, updateUrl]
  );

  const setGenre = useCallback(
    (genre: string | null) => {
      const newQuery = { ...movieQuery, genre };
      setMovieQuery(newQuery);
      updateUrl(newQuery);
    },
    [movieQuery, updateUrl]
  );

  const setSortOrder = useCallback(
    (sortOrder: string) => {
      const newQuery = { ...movieQuery, sortOrder };
      setMovieQuery(newQuery);
      updateUrl(newQuery);
    },
    [movieQuery, updateUrl]
  );

  const setSortDirection = useCallback(
    (desc: boolean) => {
      const newQuery = { ...movieQuery, sortDesc: desc };
      setMovieQuery(newQuery);
      updateUrl(newQuery);
    },
    [movieQuery, updateUrl]
  );

  const setSorting = useCallback(
    (order: string, desc: boolean) => {
      const newQuery = { ...movieQuery, sortOrder: order, sortDesc: desc };
      setMovieQuery(newQuery);
      updateUrl(newQuery);
    },
    [movieQuery, updateUrl]
  );

  const setRatingImdb = useCallback(
    (rating: number | null) => {
      const newQuery = { ...movieQuery, rating_imdb: rating };
      setMovieQuery(newQuery);
      updateUrl(newQuery);
    },
    [movieQuery, updateUrl]
  );

  const setRatingTomatoes = useCallback(
    (rating: number | null) => {
      const newQuery = { ...movieQuery, rating_rotten_tomatoes: rating };
      setMovieQuery(newQuery);
      updateUrl(newQuery);
    },
    [movieQuery, updateUrl]
  );

  const setRatingMetacritic = useCallback(
    (rating: number | null) => {
      const newQuery = { ...movieQuery, rating_metacritic: rating };
      setMovieQuery(newQuery);
      updateUrl(newQuery);
    },
    [movieQuery, updateUrl]
  );

  const setYear = useCallback(
    (year: number | null) => {
      const newQuery = { ...movieQuery, year };
      setMovieQuery(newQuery);
      updateUrl(newQuery);
    },
    [movieQuery, updateUrl]
  );

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
