# Next.js App Router

This directory contains the application routes and page components using Next.js App Router.

## 📂 Directory Structure

```
app/
├── (auth)/              # Authentication-related routes (route group)
│   ├── login/           # Login page
│   │   └── page.tsx     # Login page component
│   ├── signup/          # Signup page
│   │   └── page.tsx     # Signup page component
│   └── layout.tsx       # Layout for auth pages
├── movies/              # Movie-related routes
│   ├── [id]/            # Dynamic route for movie details
│   │   └── page.tsx     # Movie detail page
│   └── page.tsx         # Movies list page
├── actors/              # Actor-related routes
│   ├── [id]/            # Dynamic route for actor details
│   │   └── page.tsx     # Actor detail page
│   └── page.tsx         # Actors list page
├── profile/             # User profile routes
│   └── page.tsx         # Profile page
├── search/              # Search results page
│   └── page.tsx         # Search page
├── api/                 # API routes
│   └── ...              # API handlers
├── layout.tsx           # Root layout
├── page.tsx             # Home page
├── globals.css          # Global styles
└── not-found.tsx        # 404 page
```

## 🧩 App Router Conventions

### Page Components

Each route requires a `page.tsx` file that exports a React component:

```tsx
// app/movies/page.tsx
export default function MoviesPage() {
  return <MoviesPageContent />;
}
```

### Layout Components

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

### Dynamic Routes

Dynamic segments are defined with square brackets:

```tsx
// app/movies/[id]/page.tsx
export default function MovieDetail({ params }: { params: { id: string } }) {
  return <MovieDetailContent id={params.id} />;
}
```

### Route Groups

Groups in parentheses don't affect URL structure:

```
(auth)/login/page.tsx → /login
```

### Loading & Error States

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

## 🚀 Server vs. Client Components

### Server Components (Default)

```tsx
// This is a Server Component by default
export default function MoviePage() {
  // Can fetch data directly
  // No hooks allowed
  // No interactivity
  return <MovieDisplay />;
}
```

### Client Components

```tsx
"use client"; // This directive marks a Client Component

import { useState } from "react";

export default function InteractiveComponent() {
  // Can use React hooks
  const [count, setCount] = useState(0);

  return <button onClick={() => setCount(count + 1)}>Count: {count}</button>;
}
```

## 📊 Data Fetching

### Server Components

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

### Client Components

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

## 🔍 Route Handlers

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

## 📚 Related Documentation

- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [Components Directory](../components/README.md) - UI components used in pages
- [Hooks Directory](../hooks/README.md) - Hooks used in Client Components
