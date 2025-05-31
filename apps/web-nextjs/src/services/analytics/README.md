***REMOVED*** Analytics Module

This module provides comprehensive Google Analytics tracking utilities for the Next Watch application.

***REMOVED******REMOVED*** Quick Start

```typescript
import { Analytics, trackMovieEvent } from "@/services/analytics";

// Simple tracking
trackMovieEvent("like", 123, "The Matrix");

// Organized API
Analytics.movie.like(123, "The Matrix");
```

***REMOVED******REMOVED*** Available Functions

***REMOVED******REMOVED******REMOVED*** Movie Tracking

- `trackMovieEvent(action, movieId, movieTitle?)` - Track movie interactions
- Actions: `view`, `like`, `unlike`, `add_to_watchlist`, `remove_from_watchlist`, `mark_watched`, `unmark_watched`

***REMOVED******REMOVED******REMOVED*** Search Tracking

- `trackSearchEvent(query, resultsCount, filters?)` - Track search queries

***REMOVED******REMOVED******REMOVED*** Navigation Tracking

- `trackNavigationEvent(destination, source?)` - Track page navigation

***REMOVED******REMOVED******REMOVED*** Authentication Tracking

- `trackAuthEvent(action, method?)` - Track login/logout events

***REMOVED******REMOVED******REMOVED*** Feature Usage Tracking

- `trackFeatureEvent(feature, action, value?)` - Track feature interactions

***REMOVED******REMOVED******REMOVED*** Performance Tracking

- `trackPerformanceEvent(metric, value, unit?)` - Track performance metrics

***REMOVED******REMOVED******REMOVED*** Error Tracking

- `trackErrorEvent(errorType, errorMessage, errorLocation?)` - Track application errors

***REMOVED******REMOVED******REMOVED*** Page View Tracking

- `trackPageView(pagePath, pageTitle?)` - Track custom page views

***REMOVED******REMOVED*** Organized API

Use the `Analytics` object for a more organized API:

```typescript
import { Analytics } from "@/services/analytics";

// Movie interactions
Analytics.movie.view(123, "Movie Title");
Analytics.movie.like(123, "Movie Title");
Analytics.movie.addToWatchlist(123, "Movie Title");

// Search
Analytics.search.query("action movies", 25, { genre: "action" });

// Navigation
Analytics.navigation.navigate("/movies", "/home");

// Authentication
Analytics.auth.login("google");
Analytics.auth.logout();

// Features
Analytics.feature.use("search-filters", "apply", "genre:action");

// Performance
Analytics.performance.metric("page_load_time", 1200, "ms");

// Errors
Analytics.error.track("api_error", "Failed to fetch movies", "/movies");

// Page views
Analytics.page.view("/movies", "Movies Page");
```

***REMOVED******REMOVED*** Development Utilities

In development mode, additional utilities are available:

```typescript
import { analyticsDevUtils } from "@/services/analytics";

// Test all analytics events
analyticsDevUtils.testAllEvents();

// Check GA status
analyticsDevUtils.checkGAStatus();

// Send test event
analyticsDevUtils.sendTestEvent();

// Get last event (dev only)
analyticsDevUtils.getLastEvent();
```

***REMOVED******REMOVED******REMOVED*** Console Access

In development, utilities are also available in the browser console:

```javascript
// Test all events
window.analyticsDevUtils.testAllEvents();

// Check status
window.analyticsDevUtils.checkGAStatus();

// Get last event
window.lastAnalyticsEvent;
```

***REMOVED******REMOVED*** Type Safety

The module exports TypeScript types for better development experience:

```typescript
import type {
  MovieAction,
  AuthAction,
  SearchFilters,
} from "@/services/analytics";

const action: MovieAction = "like"; // ✅ Type safe
const invalidAction: MovieAction = "invalid"; // ❌ Type error
```

***REMOVED******REMOVED*** Best Practices

1. **Always include context**: Provide meaningful titles and locations
2. **Use the organized API**: `Analytics.movie.like()` is clearer than `trackMovieEvent('like')`
3. **Track user flows**: Use navigation tracking to understand user journeys
4. **Monitor performance**: Track key metrics like load times
5. **Error tracking**: Always track errors with context

***REMOVED******REMOVED*** Examples

```typescript
import { Analytics } from "@/services/analytics";

// In a movie component
const handleLike = (movie) => {
  // Your like logic
  likeMovie(movie.id);

  // Track the interaction
  Analytics.movie.like(movie.id, movie.title);
};

// In search component
const handleSearch = (query, results, filters) => {
  Analytics.search.query(query, results.length, filters);
};

// In navigation
const handleNavigation = (to, from) => {
  Analytics.navigation.navigate(to, from);
};

// Error boundary
const handleError = (error, location) => {
  Analytics.error.track("component_error", error.message, location);
};
```

***REMOVED******REMOVED*** Configuration

Analytics events are automatically logged in development mode and sent to Google Analytics in production. All events include timestamps and relevant metadata for debugging and analysis.
