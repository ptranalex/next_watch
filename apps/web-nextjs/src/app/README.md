***REMOVED*** Next.js App Router

This directory contains the application routes and page components using Next.js App Router.

***REMOVED******REMOVED*** 📂 Directory Structure

```
app/
├── (auth)/              ***REMOVED*** Authentication-related routes (route group)
│   ├── login/           ***REMOVED*** Login page
│   │   └── page.tsx     ***REMOVED*** Login page component
│   ├── signup/          ***REMOVED*** Signup page
│   │   └── page.tsx     ***REMOVED*** Signup page component
│   └── layout.tsx       ***REMOVED*** Layout for auth pages
├── movies/              ***REMOVED*** Movie-related routes
│   ├── [id]/            ***REMOVED*** Dynamic route for movie details
│   │   └── page.tsx     ***REMOVED*** Movie detail page
│   └── page.tsx         ***REMOVED*** Movies list page
├── actors/              ***REMOVED*** Actor-related routes
│   ├── [id]/            ***REMOVED*** Dynamic route for actor details
│   │   └── page.tsx     ***REMOVED*** Actor detail page
│   └── page.tsx         ***REMOVED*** Actors list page
├── profile/             ***REMOVED*** User profile routes
│   └── page.tsx         ***REMOVED*** Profile page
├── search/              ***REMOVED*** Search results page
│   └── page.tsx         ***REMOVED*** Search page
├── api/                 ***REMOVED*** API routes
│   └── ...              ***REMOVED*** API handlers
├── layout.tsx           ***REMOVED*** Root layout
├── page.tsx             ***REMOVED*** Home page
├── globals.css          ***REMOVED*** Global styles
└── not-found.tsx        ***REMOVED*** 404 page
```

***REMOVED******REMOVED*** 🧩 App Router Conventions

***REMOVED******REMOVED******REMOVED*** Page Components

Each route requires a `page.tsx` file that exports a React component:

```tsx
// app/movies/page.tsx
export default function MoviesPage() {
  return <MoviesPageContent />;
}
```

***REMOVED******REMOVED******REMOVED*** Layout Components

Layouts wrap pages and persist across routes:

```tsx
// app/layout.tsx
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <MainNavigation />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
```

***REMOVED******REMOVED******REMOVED*** Dynamic Routes

Dynamic segments are defined with square brackets:

```tsx
// app/movies/[id]/page.tsx
export default function MovieDetail({ params }: { params: { id: string } }) {
  return <MovieDetailContent id={params.id} />;
}
```

***REMOVED******REMOVED******REMOVED*** Route Groups

Groups in parentheses don't affect URL structure:

```
(auth)/login/page.tsx → /login
```

***REMOVED******REMOVED******REMOVED*** Loading & Error States

Specialized files for loading and error states:

```tsx
// app/movies/[id]/loading.tsx
export default function Loading() {
  return <MovieDetailSkeleton />;
}

// app/movies/[id]/error.tsx
export default function Error({ error }: { error: Error }) {
  return <ErrorDisplay message={error.message} />;
}
```

***REMOVED******REMOVED*** 🚀 Server vs. Client Components

***REMOVED******REMOVED******REMOVED*** Server Components (Default)

```tsx
// This is a Server Component by default
export default function MoviePage() {
  // Can fetch data directly
  // No hooks allowed
  // No interactivity
  return <MovieDisplay />;
}
```

***REMOVED******REMOVED******REMOVED*** Client Components

```tsx
"use client"; // This directive marks a Client Component

import { useState } from "react";

export default function InteractiveComponent() {
  // Can use React hooks
  const [count, setCount] = useState(0);

  return <button onClick={() => setCount(count + 1)}>Count: {count}</button>;
}
```

***REMOVED******REMOVED*** 📊 Data Fetching

***REMOVED******REMOVED******REMOVED*** Server Components

```tsx
// In a Server Component
export default async function MovieDetail({
  params,
}: {
  params: { id: string };
}) {
  // Direct data fetching in Server Components
  const movie = await MovieAPI.getById(params.id);

  return <MovieDisplay movie={movie} />;
}
```

***REMOVED******REMOVED******REMOVED*** Client Components

```tsx
"use client";

import { useMovie } from "@/hooks";

export function MovieInteractions({ movieId }: { movieId: string }) {
  // Use hooks in Client Components
  const { movie, toggleLiked } = useMovie(Number(movieId));

  return (
    <button onClick={toggleLiked}>{movie.liked ? "Unlike" : "Like"}</button>
  );
}
```

***REMOVED******REMOVED*** 🔍 Route Handlers

API routes using Route Handlers:

```tsx
// app/api/movies/route.ts
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get("query");

  // Process request
  const movies = await fetchMovies(query);

  return NextResponse.json(movies);
}
```

***REMOVED******REMOVED*** 📚 Related Documentation

- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [Components Directory](../components/README.md) - UI components used in pages
- [Hooks Directory](../hooks/README.md) - Hooks used in Client Components
