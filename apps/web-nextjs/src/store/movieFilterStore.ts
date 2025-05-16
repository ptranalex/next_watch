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
  lockedFilters: (keyof MovieFilters)[];

  // Core methods
  setFilter: <K extends keyof MovieFilters>(
    key: K,
    value: MovieFilters[K]
  ) => void;
  resetFilters: () => void;
  getFilters: () => MovieFilters;
  setSorting: (order: string, desc: boolean) => void;

  // Locking methods
  lockFilters: (keys: (keyof MovieFilters)[]) => void;
  unlockFilters: () => void;
  unlockAllFilters: () => void;
  isFilterLocked: (key: keyof MovieFilters) => boolean;
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
      lockedFilters: [],

      setFilter: (key, value) =>
        set((state) => {
          // Don't update if the filter is locked
          if (state.lockedFilters.includes(key)) {
            console.log(`Filter ${String(key)} is locked, ignoring update`);
            return state;
          }

          return {
            filters: { ...state.filters, [key]: value },
          };
        }),

      resetFilters: () =>
        set((state) => {
          // Create a new filters object starting with initialState
          const newFilters = { ...initialState };

          // Preserve values for locked filters
          state.lockedFilters.forEach((lockedKey) => {
            if (state.filters[lockedKey] !== undefined) {
              // Cast to handle the type safely
              (newFilters as any)[lockedKey] = state.filters[lockedKey];
            }
          });

          return { filters: newFilters };
        }),

      getFilters: () => get().filters,

      setSorting: (order, desc) =>
        set((state) => {
          const sortOrderLocked = state.lockedFilters.includes("sortOrder");
          const sortDescLocked = state.lockedFilters.includes("sortDesc");

          return {
            filters: {
              ...state.filters,
              sortOrder: sortOrderLocked ? state.filters.sortOrder : order,
              sortDesc: sortDescLocked ? state.filters.sortDesc : desc,
            },
          };
        }),

      // Locking methods
      lockFilters: (keys) =>
        set((state) => ({
          lockedFilters: Array.from(new Set([...state.lockedFilters, ...keys])),
        })),

      unlockFilters: () => set({ lockedFilters: [] }),

      unlockAllFilters: () => set({ lockedFilters: [] }),

      isFilterLocked: (key) => get().lockedFilters.includes(key),
    }),
    {
      name: "movie-filters",
      storage:
        typeof window !== "undefined"
          ? createJSONStorage(() => sessionStorage)
          : undefined,
      // Don't persist locked filters to storage
      partialize: (state) => ({ filters: state.filters }),
    }
  )
);

export default useMovieFilterStore;
