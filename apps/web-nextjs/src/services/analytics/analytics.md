# Google Analytics Integration

This document explains how Google Analytics is integrated into the Next Watch application using modern Next.js best practices and a consolidated architecture.

## Overview

The application uses the `@next/third-parties` package for Google Analytics integration, which is the official Next.js solution for third-party scripts. This approach provides:

- **Performance optimization** - Scripts load after hydration
- **Built-in optimization** - Automatic script loading strategies
- **Type safety** - Full TypeScript support
- **No custom providers needed** - Simple, clean integration

## Architecture

### 🏗️ **Consolidated Design (Best Practice)**

We follow a **single source of truth** pattern:

```
📁 utils/analytics.ts          # ✅ Core implementation (logging, error handling, dev tools)
📁 hooks/core/useAnalytics.ts  # ✅ Thin React wrapper (useCallback optimization)
```

**Benefits:**

- ✅ **DRY Principle** - No duplicated logic
- ✅ **Single Source of Truth** - All analytics logic in one place
- ✅ **Easy Maintenance** - Changes in one file
- ✅ **Consistent Behavior** - Same logging/error handling everywhere
- ✅ **Type Safety** - Centralized type definitions

### 🚫 **Anti-Pattern (What We Avoided)**

```
❌ Duplicated logging in both files
❌ Inconsistent error handling
❌ Multiple sources of truth
❌ Hard to maintain
```

## Setup

### 1. Package Installation

```bash
pnpm add @next/third-parties
```

### 2. Root Layout Integration

The Google Analytics component is added to the root layout (`app/layout.tsx`):

```tsx
import { GoogleAnalytics } from "@next/third-parties/google";

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
        <GoogleAnalytics gaId="G-KEFGRJ4SLR" />
      </body>
    </html>
  );
}
```

## Usage Patterns

### 🎯 **Pattern 1: useAnalytics Hook (Recommended for Components)**

**Use when:** Inside React components or custom hooks that need React context

```tsx
import { useAnalytics } from "@/services/hooks/core";

function MovieCard({ movie }) {
  const analytics = useAnalytics();

  const handleLike = () => {
    // Returns boolean indicating success
    const success = analytics.trackMovie("like", movie.id, movie.title);
    if (!success) {
      // Handle analytics failure if needed
      console.warn("Analytics tracking failed");
    }
  };

  return (
    <div>
      <button onClick={handleLike}>Like Movie</button>
    </div>
  );
}
```

### 🔧 **Pattern 2: Direct Utility Functions (For Non-React Code)**

**Use when:** Inside utility functions, middleware, or non-React code

```tsx
import { trackMovieEvent, trackSearchEvent } from "@/utils/analytics";

// In a utility function
export function processMovieAction(action, movieId, title) {
  // Some processing logic...
  const success = trackMovieEvent(action, movieId, title);
  return success;
}

// In middleware or API routes
export function middleware(request) {
  trackNavigationEvent(request.nextUrl.pathname);
}
```

## When to Use Which Pattern?

| Scenario              | Use                   | Why                                     |
| --------------------- | --------------------- | --------------------------------------- |
| React Components      | `useAnalytics()` hook | React context, useCallback optimization |
| Custom React Hooks    | `useAnalytics()` hook | Consistent with React patterns          |
| Utility Functions     | Direct imports        | No React overhead needed                |
| Middleware/API Routes | Direct imports        | No React context available              |
| Event Handlers        | `useAnalytics()` hook | Component-level tracking                |

## Available Tracking Functions

All functions return `boolean` indicating success/failure:

### Movie Interactions

- `trackMovie(action, movieId, movieTitle?)` → `boolean`
- Actions: `"view"`, `"like"`, `"unlike"`, `"add_to_watchlist"`, `"remove_from_watchlist"`, `"mark_watched"`, `"unmark_watched"`

### Search Events

- `trackSearch(query, resultsCount, filters?)` → `boolean`
- Filters: `{ genre?, year?, sortBy? }`

### Navigation

- `trackNavigation(destination, source?)` → `boolean`

### Authentication

- `trackAuth(action, method?)` → `boolean`
- Actions: `"login"`, `"logout"`, `"signup"`
- Methods: `"google"`, `"email"`

### Feature Usage

- `trackFeature(feature, action, value?)` → `boolean`

### Performance

- `trackPerformance(metric, value, unit?)` → `boolean`

### Errors

- `trackError(errorType, errorMessage, errorLocation?)` → `boolean`

### Page Views

- `trackPage(pagePath, pageTitle?)` → `boolean`
- Note: Page views are automatically tracked by the GoogleAnalytics component

## Real Examples in the Codebase

### 1. Movie Interactions (useMovieInteractions Hook)

```tsx
// ✅ Using useAnalytics hook in a custom hook
export function useMovieInteractions({ movieId, movie }) {
  const analytics = useAnalytics();

  const createMutationConfig = (config) => ({
    onSuccess: () => {
      const action = config.currentValue ? "unlike" : "like";
      analytics.trackMovie(action, movieId, movie?.title);
    },
  });
}
```

### 2. Search Page Component

```tsx
// ✅ Using useAnalytics hook in a component
export function SearchPage() {
  const analytics = useAnalytics();

  useEffect(() => {
    if (query && movies.length > 0) {
      analytics.trackSearch(query, movies.length, {
        genre: genreId ? genreNames[genreId] : undefined,
        year,
        sortBy,
      });
    }
  }, [query, movies, genreId, year, sortBy, analytics]);
}
```

### 3. Movie Card Component

```tsx
// ✅ Using useAnalytics hook for user interactions
export function MovieCard({ movie }) {
  const analytics = useAnalytics();

  const handleClick = () => {
    const success = analytics.trackMovie("view", movie.id, movie.title);
    if (success) {
      // Navigate to movie detail...
    }
  };

  return <div onClick={handleClick}>{/* Movie card content */}</div>;
}
```

### 4. Authentication Utility

```tsx
// ✅ Using direct imports in utility functions
import { trackAuthEvent } from "@/utils/analytics";

export async function loginUser(method: "google" | "email") {
  // Login logic...
  const tracked = trackAuthEvent("login", method);
  return { success: true, tracked };
}
```

## Development Features

### 🧪 **Testing Utilities**

```javascript
// Test all analytics events at once
window.analyticsDevUtils.testAllEvents();

// Check GA status
window.analyticsDevUtils.checkGAStatus();

// Get the last event sent
window.analyticsDevUtils.getLastEvent();
```

### 📊 **Enhanced Logging**

In development mode, you'll see:

```bash
📊 Analytics Event (DEV) { event: "movie_interaction", movie_action: "like", ... }
🔍 Google Analytics Event
  Event Data: { event: "movie_interaction", ... }
  Timestamp: 2024-01-15T10:30:00.000Z
  Environment: development
```

### 🔍 **Error Handling**

```tsx
const success = analytics.trackMovie("like", movieId, movieTitle);
if (!success) {
  // Analytics failed, but app continues working
  console.warn("Analytics tracking failed");
}
```

## Best Practices

### 1. **Use the Consolidated Architecture**

- ✅ All logic in `utils/analytics.ts`
- ✅ Hook is just a thin wrapper
- ✅ No duplicated code

### 2. **Choose the Right Pattern**

- **Components/Hooks**: Use `useAnalytics()` hook
- **Utilities/Middleware**: Use direct imports

### 3. **Handle Return Values**

```tsx
// Good - Check success
const success = analytics.trackMovie("like", movieId, movieTitle);

// Better - Handle failure
const success = analytics.trackMovie("like", movieId, movieTitle);
if (!success) {
  // Maybe retry or log for debugging
}
```

### 4. **Track User Intent**

Track meaningful user actions, not just technical events:

- ✅ User likes a movie
- ✅ User searches for content
- ❌ Component mounted
- ❌ API call started

### 5. **Include Context**

Provide relevant context with events:

```tsx
// Good
analytics.trackMovie("view", movie.id, movie.title);

// Better
analytics.trackSearch("batman", 25, {
  genre: "action",
  year: 2024,
  sortBy: "popularity",
});
```

## Development vs Production

### Development

- Detailed console logs with 📊 emoji
- `window.analyticsDevUtils` for testing
- Enhanced error reporting
- `window.lastAnalyticsEvent` tracking

### Production

- Minimal logging (debug level)
- Error tracking without console spam
- Performance optimized

## Troubleshooting

### Events Not Appearing

1. Check that the GA tracking ID is correct
2. Verify the `@next/third-parties` package is installed
3. Check browser console for errors
4. Use GA Real-time reports to verify events

### TypeScript Errors

Make sure to import types correctly:

```tsx
import { useAnalytics } from "@/services/hooks/core";
```

### Performance Issues

The `@next/third-parties` package automatically optimizes script loading. If you experience issues:

1. Ensure you're not loading GA scripts manually elsewhere
2. Check for conflicting analytics implementations
3. Monitor Core Web Vitals in GA

## Migration Guide

If you have existing analytics code:

### ❌ Old Pattern (Duplicated Logic)

```tsx
// Don't do this
const trackEvent = () => {
  try {
    logger.debug("Tracking...");
    sendGAEvent(data);
    logger.info("Success");
  } catch (error) {
    logger.error("Failed");
  }
};
```

### ✅ New Pattern (Consolidated)

```tsx
// Do this instead
import { trackMovieEvent } from "@/utils/analytics";

const success = trackMovieEvent("like", movieId, movieTitle);
// All logging, error handling, and dev tools are built-in
```

This consolidated architecture ensures maintainable, consistent, and reliable analytics tracking! 🎉
