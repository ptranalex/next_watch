***REMOVED*** API Services

This directory contains the API services for the Next Watch web application. These services are responsible for communicating with the backend services.

***REMOVED******REMOVED*** API Client Consolidation

We've consolidated our API clients to use a single client that communicates with the BFF (Backend For Frontend) API. This simplifies our architecture and ensures consistent API interactions.

***REMOVED******REMOVED******REMOVED*** Key Changes

1. **Single API Client**: We now use a single axios-based API client configured to point to the BFF API.
2. **Consolidated Directory Structure**: All API-related code is organized into domain-specific directories.
3. **Deprecated BFF Client**: The separate BFF client has been deprecated, and its functionality has been integrated into the core API client.

***REMOVED******REMOVED*** Directory Structure

```
api/
├── core/               ***REMOVED*** Core API client and utilities
│   ├── api-client.ts   ***REMOVED*** Main API client with axios
│   └── errors.ts       ***REMOVED*** Error types and handling
├── bff/                ***REMOVED*** Deprecated BFF client (for backward compatibility)
├── auth/               ***REMOVED*** Authentication API
├── movies/             ***REMOVED*** Movie-related API
├── actors/             ***REMOVED*** Actor-related API
├── genres/             ***REMOVED*** Genre-related API
├── search/             ***REMOVED*** Search API
├── user/               ***REMOVED*** User profile and interactions API
└── common/             ***REMOVED*** Shared types and utilities
```

***REMOVED******REMOVED*** Usage

```typescript
// Import the API client and utilities
import { fetchData, MovieAPI, ActorAPI, AuthAPI } from "@/services/api";

// Use domain-specific APIs
const movies = await MovieAPI.getMovies({ genre_id: 28 });
const actor = await ActorAPI.getById(123);
const isLoggedIn = await AuthAPI.isAuthenticated();

// Or use the generic utilities directly
const data = await fetchData("/some/endpoint");
```

***REMOVED******REMOVED*** Migration Guide

If you're still using the deprecated BFF client, migrate to the core API client:

***REMOVED******REMOVED******REMOVED*** Before

```typescript
import { bffFetchData } from "@/services/api/bff/bff-client";

const data = await bffFetchData("/bff/v1/endpoint");
```

***REMOVED******REMOVED******REMOVED*** After

```typescript
import { fetchData } from "@/services/api";

const data = await fetchData("/bff/v1/endpoint");
```

***REMOVED******REMOVED*** Error Handling

The API client includes comprehensive error handling with specific error types:

```typescript
import {
  fetchData,
  ValidationError,
  AuthError,
  NetworkError,
  APIError,
  CacheHitError,
} from "@/services/api";

try {
  const data = await fetchData("/api/endpoint");
} catch (error) {
  if (error instanceof ValidationError) {
    // Handle validation errors (HTTP 400)
    console.error("Validation error:", error.message);
  } else if (error instanceof AuthError) {
    // Handle authentication errors (HTTP 401, 403)
    console.error("Auth error:", error.message);
    // Check if token expired
    if (error.isTokenExpired) {
      // Handle token expiration
    }
  } else if (error instanceof NetworkError) {
    // Handle network connectivity errors
    console.error("Network error:", error.message);
  } else if (error instanceof APIError) {
    // Handle general API errors (other HTTP errors)
    console.error("API error:", error.message);
  } else if (error instanceof CacheHitError) {
    // This should be caught by the interceptor, not by user code
  } else {
    // Handle unexpected errors
    console.error("Unexpected error:", error);
  }
}
```
