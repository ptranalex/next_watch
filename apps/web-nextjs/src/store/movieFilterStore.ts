import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { createLogger } from "@/utils/logging";

// Create logger for this store
const logger = createLogger("movieFilterStore");

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
            logger.debug(`Filter ${String(key)} is locked, ignoring update`);
            return state;
          }

          logger.debug(`Setting filter ${String(key)} to ${value}`);
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
              logger.debug(
                `Preserving locked filter ${String(lockedKey)}: ${
                  state.filters[lockedKey]
                }`
              );
            }
          });

          logger.info(
            "Resetting filters to initial state (preserving locked filters)"
          );
          return { filters: newFilters };
        }),

      getFilters: () => get().filters,

      setSorting: (order, desc) =>
        set((state) => {
          const sortOrderLocked = state.lockedFilters.includes("sortOrder");
          const sortDescLocked = state.lockedFilters.includes("sortDesc");

          if (sortOrderLocked) {
            logger.debug("Sort order is locked, ignoring update");
          }
          if (sortDescLocked) {
            logger.debug("Sort direction is locked, ignoring update");
          }

          if (!sortOrderLocked || !sortDescLocked) {
            logger.info(
              `Setting sort to ${order} (${desc ? "descending" : "ascending"})`
            );
          }

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
        set((state) => {
          logger.info(`Locking filters: ${keys.join(", ")}`);
          return {
            lockedFilters: Array.from(
              new Set([...state.lockedFilters, ...keys])
            ),
          };
        }),

      unlockFilters: () => {
        logger.info("Unlocking all filters");
        set({ lockedFilters: [] });
      },

      unlockAllFilters: () => {
        logger.info("Unlocking all filters");
        set({ lockedFilters: [] });
      },

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
