***REMOVED*** BFF API Integration

***REMOVED******REMOVED*** Overview

The Backend for Frontend (BFF) API layer provides an optimized interface between the Next.js frontend and the backend services. It aggregates data, reduces API calls, and provides better user experience.

***REMOVED******REMOVED*** Architecture

```
Frontend (Next.js) → BFF API (FastAPI) → Backend API + Auth API
```

***REMOVED******REMOVED*** Key Benefits

1. **Reduced API Calls**: Multiple backend calls are aggregated into single BFF calls
2. **Better Performance**: Data is pre-aggregated and optimized for frontend needs
3. **User Context**: Authentication and user-specific data is handled centrally
4. **Standardized Pagination**: All endpoints use consistent pagination format
5. **Type Safety**: Full TypeScript support with proper type definitions

***REMOVED******REMOVED*** Standardized Pagination Format

All BFF endpoints return paginated data in this format:

```typescript
{
  total: number;         // Total number of items
  page: number;          // Current page number
  per_page: number;      // Items per page
  total_pages: number;   // Total number of pages
  has_next: boolean;     // Whether there's a next page
  has_prev: boolean;     // Whether there's a previous page
  results: T[];          // Array of items
}
```

***REMOVED******REMOVED*** Available Services

***REMOVED******REMOVED******REMOVED*** Movies API

```typescript
import { BFFMoviesAPI } from "@/services/api";

// Get movies with filters
const movies = await BFFMoviesAPI.getMovies({
  page: 1,
  limit: 20,
  genre_id: 28,
  sort_by: "imdb_rating",
  sort_desc: true,
  imdb_rating: 7.0,
});

// Get movie detail with cast, trailers, user interactions
const movieDetail = await BFFMoviesAPI.getMovieDetail(123);

// Get home screen data
const homeData = await BFFMoviesAPI.getHomeScreen(userId);

// Search movies
const searchResults = await BFFMoviesAPI.searchMovies("Inception");
```

***REMOVED******REMOVED******REMOVED*** Authentication API

```typescript
import { BFFAuthAPI } from "@/services/api";

// Login
const authResponse = await BFFAuthAPI.login({
  email: "user@example.com",
  password: "password",
});

// Register
const registerResponse = await BFFAuthAPI.register({
  email: "user@example.com",
  password: "password",
  name: "John Doe",
});

// Get current user
const user = await BFFAuthAPI.getCurrentUser();

// Check if authenticated
const isAuth = BFFAuthAPI.isAuthenticated();
```

***REMOVED******REMOVED*** Configuration

Set these environment variables:

```env
NEXT_PUBLIC_BFF_API_URL=http://localhost:8001
NEXT_PUBLIC_BFF_API_TIMEOUT=15000
```

***REMOVED******REMOVED*** Migration from Direct Backend Calls

***REMOVED******REMOVED******REMOVED*** Before (Direct Backend API)

```typescript
import { MovieAPI } from "@/services/api";

const movies = await MovieAPI.getMovies({
  page: 1,
  pageSize: 20,
  genre_id: 28,
});
// Result: { movies: Movie[], total: number, page: number, page_size: number }
```

***REMOVED******REMOVED******REMOVED*** After (BFF API)

```typescript
import { BFFMoviesAPI } from "@/services/api";

const movies = await BFFMoviesAPI.getMovies({
  page: 1,
  limit: 20,
  genre_id: 28,
});
// Result: { total: number, page: number, per_page: number, total_pages: number, has_next: boolean, has_prev: boolean, results: Movie[] }
```

***REMOVED******REMOVED*** Error Handling

The BFF client automatically handles:

- Authentication token management
- Error logging and debugging
- Network error retry (planned)
- Response caching (planned)

***REMOVED******REMOVED*** Type Safety

All BFF services are fully typed:

```typescript
import type {
  BFFMovieListResponse,
  MovieDetailData,
  HomeScreenData,
  UserInteractions,
} from "@/services/api";
```

***REMOVED******REMOVED*** Development

When developing locally, ensure both services are running:

```bash
***REMOVED*** Backend API
cd apps/backend-api && poetry run uvicorn backend_api.main:app --reload --port 8000

***REMOVED*** BFF API
cd apps/bff-api && poetry run uvicorn bff_api.main:app --reload --port 8001

***REMOVED*** Frontend
cd apps/web-nextjs && pnpm dev
```
