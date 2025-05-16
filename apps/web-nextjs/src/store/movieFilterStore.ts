import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

interface MovieFilters {
  imdb_rating?: number;
  rotten_tomatoes_rating?: number;
  metacritic_rating?: number;
  year?: number;
  sortOrder?: string;
  sortDesc?: boolean;
}

interface MovieFilterStore {
  filters: MovieFilters;
  setFilter: <K extends keyof MovieFilters>(
    key: K,
    value: MovieFilters[K]
  ) => void;
  resetFilters: () => void;
  getFilters: () => MovieFilters;
  setSorting: (order: string, desc: boolean) => void;
}

const initialState: MovieFilters = {
  imdb_rating: undefined,
  rotten_tomatoes_rating: undefined,
  metacritic_rating: undefined,
  year: undefined,
  sortOrder: "release_date",
  sortDesc: true,
};

const useMovieFilterStore = create<MovieFilterStore>()(
  persist(
    (set, get) => ({
      filters: initialState,

      setFilter: (key, value) =>
        set((state) => ({
          filters: { ...state.filters, [key]: value },
        })),

      resetFilters: () => {
        console.log("resetFilters");
        set({ filters: initialState });
      },

      getFilters: () => get().filters,

      setSorting: (order, desc) =>
        set((state) => ({
          filters: { ...state.filters, sortOrder: order, sortDesc: desc },
        })),
    }),
    {
      name: "movie-filters", // 🧠 storage key
      storage:
        typeof window !== "undefined"
          ? createJSONStorage(() => sessionStorage)
          : undefined,
    }
  )
);

export default useMovieFilterStore;
