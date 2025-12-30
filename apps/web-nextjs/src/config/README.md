# Application Configuration

This directory contains configuration settings and feature flags for the NextWatch application.

## 📂 Directory Structure

```
config/
├── index.ts           # Main configuration export
├── api.ts             # API-related configuration
├── features.ts        # Feature flags and toggles
├── themes.ts          # Theme configuration
└── constants.ts       # Application constants
```

## 🔧 Configuration Pattern

The application uses a centralized configuration pattern:

```typescript
// config/index.ts
import { apiConfig } from "./api";
import { featureFlags } from "./features";

export const CONFIG = {
  // API Configuration
  api: apiConfig,

  // Feature Flags
  features: featureFlags,

  // App Settings
  app: {
    name: "NextWatch",
    version: "1.0.0",
    environment: process.env.NODE_ENV,
  },

  // Default Pagination
  pagination: {
    defaultPageSize: 20,
    maxPageSize: 100,
  },
};

// Default export for convenience
export default CONFIG;
```

## 🚩 Feature Flags

Feature flags enable or disable application features:

```typescript
// config/features.ts
export const FEATURES = {
  // Movie Features
  ENABLE_MOVIE_RATINGS: true,
  SHOW_MOVIE_TRAILERS: true,
  ENABLE_WATCHLIST: true,

  // User Features
  ENABLE_USER_PROFILES: true,
  ALLOW_SOCIAL_LOGIN: true,

  // UI Features
  ENABLE_DARK_MODE: true,
  SHOW_SEARCH_SUGGESTIONS: true,
};

// Function to check if a feature is enabled
export function isFeatureEnabled(featureName: keyof typeof FEATURES): boolean {
  return FEATURES[featureName] === true;
}
```

## 🌐 API Configuration

Configuration for API endpoints and behavior:

```typescript
// config/api.ts
export const apiConfig = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  timeout: 10000, // 10 seconds

  // Endpoint paths
  endpoints: {
    movies: "/api/movies",
    actors: "/api/actors",
    genres: "/api/genres",
    search: "/api/search",
    auth: "/api/auth",
  },

  // Default headers
  defaultHeaders: {
    "Content-Type": "application/json",
  },
};
```

## 🎨 Theme Configuration

Configuration for UI themes:

```typescript
// config/themes.ts
export const themeConfig = {
  // Color scheme
  colors: {
    primary: {
      50: "#e3f2fd",
      100: "#bbdefb",
      500: "#2196f3",
      800: "#0d47a1",
    },
    // ... other colors
  },

  // Typography
  fonts: {
    body: "Inter, system-ui, sans-serif",
    heading: "Inter, system-ui, sans-serif",
  },

  // Component theme overrides
  components: {
    Button: {
      // Button theme customizations
    },
    // ... other component overrides
  },
};
```

## 🔤 Constants

Application-wide constants:

```typescript
// config/constants.ts
export const APP_CONSTANTS = {
  // Storage keys
  STORAGE_KEYS: {
    AUTH_TOKEN: "auth_token",
    USER_PREFERENCES: "user_prefs",
    THEME: "theme",
  },

  // Date formats
  DATE_FORMATS: {
    DEFAULT: "MM/DD/YYYY",
    DISPLAY: "MMMM D, YYYY",
    ISO: "YYYY-MM-DD",
  },

  // Navigation
  ROUTES: {
    HOME: "/",
    MOVIES: "/movies",
    MOVIE_DETAIL: (id: string | number) => `/movies/${id}`,
    ACTORS: "/actors",
    ACTOR_DETAIL: (id: string | number) => `/actors/${id}`,
    PROFILE: "/profile",
    LOGIN: "/login",
    SIGNUP: "/signup",
  },
};
```

## 🔄 Usage

Import configuration values from the main config export:

```typescript
import { CONFIG } from "@/config";

// Use configuration values
const apiUrl = CONFIG.api.baseUrl;
const pageSize = CONFIG.pagination.defaultPageSize;
```

For feature flags:

```typescript
import { FEATURES, isFeatureEnabled } from "@/config/features";

// Check if a feature is enabled
if (isFeatureEnabled("ENABLE_MOVIE_RATINGS")) {
  // Render movie ratings component
}

// Or access directly
if (FEATURES.SHOW_MOVIE_TRAILERS) {
  // Show movie trailers
}
```

## 🔐 Environment Variables

Configuration can use environment variables from `.env.local`:

```
# .env.local
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_ENABLE_ANALYTICS=true
```

Access in configuration:

```typescript
// Access environment variables
const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const enableAnalytics = process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === "true";
```

## 📚 Related Documentation

- [Next.js Environment Variables](https://nextjs.org/docs/basic-features/environment-variables)
- [Feature Flag Best Practices](https://martinfowler.com/articles/feature-toggles.html)
