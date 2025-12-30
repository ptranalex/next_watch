# Global State Management

This directory contains global state management logic using Zustand for the NextWatch application.

## 📂 Directory Structure

```
store/
├── auth.ts            # Authentication state
├── theme.ts           # Theme preferences state
├── movieQuery.ts      # Movie filtering and query state
├── notifications.ts   # Notification state
└── index.ts           # Re-export of all stores
```

## 🧩 Store Pattern

The application uses Zustand for state management with a consistent pattern:

```typescript
// store/example.ts
import { create } from "zustand";

// Define store state interface
interface ExampleState {
  // State properties
  count: number;

  // Actions
  increment: () => void;
  decrement: () => void;
  reset: () => void;
}

// Create store with state and actions
const useExampleStore = create<ExampleState>((set) => ({
  // Initial state
  count: 0,

  // Actions
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
  reset: () => set({ count: 0 }),
}));

export default useExampleStore;
```

## 🔐 Authentication Store

Manages user authentication state:

```typescript
// store/auth.ts
import { create } from "zustand";
import { AuthUser } from "@/domain/entities";

interface AuthState {
  // State
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  signup: (userData: SignupData) => Promise<void>;
  clearError: () => void;
  loadUser: () => Promise<void>;
}

const useAuthStore = create<AuthState>((set) => ({
  // Initial state
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  // Actions
  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      // API call logic
      const user = await authService.login(email, password);
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ error: getErrorMessage(error), isLoading: false });
    }
  },

  // Other action implementations...
}));

export default useAuthStore;
```

## 🎨 Theme Store

Manages theme preferences:

```typescript
// store/theme.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";

interface ThemeState {
  // State
  colorMode: "light" | "dark" | "system";

  // Actions
  setColorMode: (mode: "light" | "dark" | "system") => void;
  toggleColorMode: () => void;
}

const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      // Initial state
      colorMode: "system",

      // Actions
      setColorMode: (colorMode) => set({ colorMode }),
      toggleColorMode: () =>
        set((state) => ({
          colorMode: state.colorMode === "light" ? "dark" : "light",
        })),
    }),
    {
      name: "theme-storage",
    }
  )
);

export default useThemeStore;
```

## 🔍 Movie Query Store

Manages movie search and filter state:

```typescript
// store/movieQuery.ts
import { create } from "zustand";

interface MovieQuery {
  search?: string;
  genres?: number[];
  year?: number;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
  imdb_rating?: number;
}

interface MovieQueryState {
  // State
  movieQuery: MovieQuery;

  // Actions
  setSearch: (search: string) => void;
  setGenres: (genres: number[]) => void;
  setYear: (year: number) => void;
  setSortBy: (sortBy: string) => void;
  setSortOrder: (sortOrder: "asc" | "desc") => void;
  setRatingImdb: (rating: number) => void;
  resetFilters: () => void;
}

const initialState: MovieQuery = {
  search: "",
  genres: [],
  year: 0,
  sortBy: "popularity",
  sortOrder: "desc",
  imdb_rating: 0,
};

const useMovieQueryStore = create<MovieQueryState>((set) => ({
  // Initial state
  movieQuery: initialState,

  // Actions
  setSearch: (search) =>
    set((state) => ({
      movieQuery: { ...state.movieQuery, search },
    })),

  // Other action implementations...

  resetFilters: () => set({ movieQuery: initialState }),
}));

export default useMovieQueryStore;
```

## 🔔 Notification Store

Manages application notifications:

```typescript
// store/notifications.ts
import { create } from "zustand";

type NotificationType = "info" | "success" | "warning" | "error";

interface Notification {
  id: string;
  message: string;
  type: NotificationType;
  duration?: number;
}

interface NotificationState {
  // State
  notifications: Notification[];

  // Actions
  addNotification: (notification: Omit<Notification, "id">) => void;
  removeNotification: (id: string) => void;
  clearAllNotifications: () => void;
}

const useNotificationStore = create<NotificationState>((set) => ({
  // Initial state
  notifications: [],

  // Actions
  addNotification: (notification) =>
    set((state) => ({
      notifications: [
        ...state.notifications,
        { ...notification, id: generateId() },
      ],
    })),

  removeNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter(
        (notification) => notification.id !== id
      ),
    })),

  clearAllNotifications: () => set({ notifications: [] }),
}));

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substring(2);
}

export default useNotificationStore;
```

## 🔄 Using Stores in Components

Import and use stores in your components:

```tsx
import { useAuthStore, useThemeStore } from "@/store";
import { Navigate } from "react-router-dom";

function ProfilePage() {
  const { user, isAuthenticated } = useAuthStore();
  const { colorMode, toggleColorMode } = useThemeStore();

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return (
    <div>
      <h1>Profile: {user?.name}</h1>
      <button onClick={toggleColorMode}>
        Switch to {colorMode === "light" ? "Dark" : "Light"} Mode
      </button>
      {/* Rest of component */}
    </div>
  );
}
```

## 🔗 Store Composition

For complex state, compose multiple stores:

```tsx
import { useCallback } from "react";
import { useAuthStore, useMovieQueryStore } from "@/store";

function MovieSearch() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const { movieQuery, setSearch, setGenres } = useMovieQueryStore();

  const handleSearch = useCallback(
    (query: string) => {
      setSearch(query);
      // Do something with authentication state if needed
      if (isAuthenticated) {
        // Save search history to user profile, etc.
      }
    },
    [isAuthenticated, setSearch]
  );

  return (
    <div>
      <input
        value={movieQuery.search}
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="Search movies..."
      />
      {/* Rest of component */}
    </div>
  );
}
```

## 🧪 Testing Stores

Test store logic in isolation:

```typescript
import { act, renderHook } from "@testing-library/react-hooks";
import useCounterStore from "./counterStore";

describe("Counter Store", () => {
  it("should initialize with count=0", () => {
    const { result } = renderHook(() => useCounterStore());
    expect(result.current.count).toBe(0);
  });

  it("should increment count", () => {
    const { result } = renderHook(() => useCounterStore());

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it("should reset count", () => {
    const { result } = renderHook(() => useCounterStore());

    act(() => {
      result.current.increment();
      result.current.increment();
      result.current.reset();
    });

    expect(result.current.count).toBe(0);
  });
});
```

## 📚 Related Documentation

- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [React Query](https://tanstack.com/query) - For server state management
- [Domain Layer](../domain/README.md) - Domain entities used in stores
