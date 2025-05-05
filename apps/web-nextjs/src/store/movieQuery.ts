import { create } from "zustand";

interface MovieQuery {
  imdb_rating?: number;
  rotten_tomatoes_rating?: number;
  metacritic_rating?: number;
  year?: number;
  sortOrder?: string;
}

interface MovieQueryStore {
  movieQuery: MovieQuery;
  setRatingImdb: (rating: number) => void;
  setRatingTomatoes: (rating: number) => void;
  setRatingMetacritic: (rating: number) => void;
  setYear: (year: number) => void;
  setSortOrder: (order: string) => void;
  resetFilters: () => void;
}

const initialState: MovieQuery = {
  imdb_rating: 0,
  rotten_tomatoes_rating: 0,
  metacritic_rating: 0,
  year: 0,
  sortOrder: "released",
};

const useMovieQueryStore = create<MovieQueryStore>((set) => ({
  movieQuery: initialState,
  setRatingImdb: (rating) =>
    set((state) => ({
      movieQuery: { ...state.movieQuery, imdb_rating: rating },
    })),
  setRatingTomatoes: (rating) =>
    set((state) => ({
      movieQuery: { ...state.movieQuery, rotten_tomatoes_rating: rating },
    })),
  setRatingMetacritic: (rating) =>
    set((state) => ({
      movieQuery: { ...state.movieQuery, metacritic_rating: rating },
    })),
  setYear: (year) =>
    set((state) => ({
      movieQuery: { ...state.movieQuery, year },
    })),
  setSortOrder: (order) =>
    set((state) => ({
      movieQuery: { ...state.movieQuery, sortOrder: order },
    })),
  resetFilters: () => set({ movieQuery: initialState }),
}));

export default useMovieQueryStore;
