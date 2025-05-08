***REMOVED*** NextWatch Web Application

A modern movie tracking web application built with Next.js, TypeScript, and Chakra UI.

***REMOVED******REMOVED*** 📋 Overview

NextWatch Web is the frontend application for the NextWatch platform, allowing users to:

- Discover and search for movies
- Track watched, liked, and watchlist movies
- View movie details, trailers, and cast information
- Manage user profiles and preferences

***REMOVED******REMOVED*** 🚀 Getting Started

***REMOVED******REMOVED******REMOVED*** Prerequisites

- Node.js 16+ and npm
- Access to the NextWatch backend API (or mock data)

***REMOVED******REMOVED******REMOVED*** Installation

```bash
***REMOVED*** Install dependencies
npm install

***REMOVED*** Set up environment variables
cp .env.example .env.local
***REMOVED*** Edit .env.local to configure your environment

***REMOVED*** Start development server
npm run dev
```

***REMOVED******REMOVED******REMOVED*** Docker Deployment

The application includes a Docker configuration for containerized deployment:

```bash
***REMOVED*** Build Docker image
docker build -t web-nextjs -f apps/web-nextjs/Dockerfile .

***REMOVED*** Run Docker container
docker run -d -p 3000:3000 --name web-nextjs-app web-nextjs
```

***REMOVED******REMOVED******REMOVED******REMOVED*** Docker Architecture

The Docker setup uses a specially configured development mode that:

- Avoids static generation issues with Next.js in production mode
- Correctly handles React hooks like useSearchParams with proper Suspense boundaries
- Provides a secure environment with non-root users
- Reduces container size through careful layer management

***REMOVED******REMOVED******REMOVED******REMOVED*** Docker Environment Variables

- `NODE_ENV=development` - Uses development mode for best compatibility
- `NEXT_TELEMETRY_DISABLED=1` - Disables Next.js telemetry
- `PORT=3000` - Sets the internal container port

***REMOVED******REMOVED******REMOVED*** Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build for production
- `npm start` - Run the production build
- `npm run lint` - Run ESLint
- `npm run docker-build` - Custom build script optimized for Docker deployment

***REMOVED******REMOVED*** 🏗️ Architecture

NextWatch follows **Clean Architecture** principles with a domain-driven approach:

```
src/
├── app/               ***REMOVED*** Next.js App Router pages
├── components/        ***REMOVED*** React components
├── domain/            ***REMOVED*** Domain entities and business logic
│   └── entities/      ***REMOVED*** Core data structures and type definitions
├── hooks/             ***REMOVED*** React hooks
│   ├── core/          ***REMOVED*** App-wide hooks (auth, etc.)
│   ├── domain/        ***REMOVED*** Domain-specific hooks
│   └── ui/            ***REMOVED*** UI utility hooks
├── services/          ***REMOVED*** External services integration
├── store/             ***REMOVED*** Global state management
└── utils/             ***REMOVED*** Utility functions
```

***REMOVED******REMOVED******REMOVED*** Key Architectural Concepts

1. **Domain Layer** - Core business entities independent of UI/framework
2. **Hooks Layer** - React-specific integration with domain logic
3. **Services Layer** - External API communication
4. **Components** - UI presentation logic

***REMOVED******REMOVED*** 📚 Documentation Structure

The codebase includes detailed documentation organized by feature area:

- `/src/domain/README.md` - Domain layer architecture and usage
- `/src/hooks/README.md` - React hooks organization and best practices
- `/src/services/README.md` - API services documentation

***REMOVED******REMOVED*** 🔄 Data Flow

1. **Components** use **Hooks** to interact with data
2. **Hooks** call **Services** to fetch or update data
3. **Services** communicate with backend APIs
4. Data is transformed to/from **Domain Entities** for use in the UI

***REMOVED******REMOVED*** 🧪 Testing

```bash
***REMOVED*** Run tests
npm test

***REMOVED*** Run tests with coverage
npm test -- --coverage
```

***REMOVED******REMOVED*** 📦 Dependencies

- [Next.js](https://nextjs.org/) - React framework
- [Chakra UI](https://chakra-ui.com/) - Component library
- [React Query](https://tanstack.com/query) - Data fetching and caching
- [Zustand](https://github.com/pmndrs/zustand) - State management

***REMOVED******REMOVED*** 🤝 Contributing

1. Ensure you understand the architecture and file organization
2. Follow existing code patterns and conventions
3. Add appropriate documentation for new features
4. Verify all tests pass before submitting pull requests

***REMOVED******REMOVED*** 📄 License

This project is licensed under the MIT License

***REMOVED******REMOVED*** URL Parameter Handling

The application uses a custom hook called `useUrlParams` for handling URL parameters safely in both server and client components. This approach solves the common SSR/hydration issues with `useSearchParams` in Next.js.

***REMOVED******REMOVED******REMOVED*** Using the `useUrlParams` hook

```tsx
import { useUrlParams } from "@/hooks/navigation/useUrlParams";

function MyComponent() {
  // Specify expected parameter types
  const { params, updateParams, setParam } = useUrlParams<{
    search?: string;
    page?: number;
    filter?: boolean;
  }>();

  // Access URL params with proper typing
  const searchTerm = params.search || "";
  const currentPage = params.page || 1;

  // Update single parameter
  const handleSearch = (term: string) => {
    setParam("search", term);
  };

  // Update multiple parameters at once
  const resetFilters = () => {
    updateParams({
      search: "",
      page: 1,
    });
  };

  return (
    <div>
      <p>Current search: {searchTerm}</p>
      <p>Page: {currentPage}</p>
      <button onClick={() => handleSearch("new term")}>Search</button>
      <button onClick={resetFilters}>Reset</button>
    </div>
  );
}
```

***REMOVED******REMOVED******REMOVED*** Benefits of this approach

1. **Type safety**: Parameters are properly typed
2. **Server-side rendering compatible**: Works in both SSR and client environments
3. **No hydration errors**: Handles the hydration process correctly
4. **No suspense boundaries needed**: Eliminates the need for wrapping components in suspense boundaries
5. **Production build compatible**: Works correctly in production builds without special accommodations

***REMOVED******REMOVED*** Sustainable Docker Strategy

For the most sustainable Docker deployment, we have two main approaches:

***REMOVED******REMOVED******REMOVED*** Approach 1: Production Build with useUrlParams

Use our custom `useUrlParams` hook throughout the codebase, which safely handles URL parameters without requiring Suspense boundaries. This approach works with proper static generation and can use a standard production Dockerfile.

***REMOVED******REMOVED******REMOVED*** Approach 2: Development Server Mode for Production

In some cases where you can't update all component instances, running in development mode can provide a more flexible solution:

```dockerfile
***REMOVED*** Simplified Dockerfile for Next.js
FROM node:20-alpine

***REMOVED*** Setup app directory
WORKDIR /app

***REMOVED*** Install dependencies
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm install --frozen-lockfile

***REMOVED*** Copy application code
COPY . .

***REMOVED*** Configure for development mode
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

***REMOVED*** Start the development server
CMD ["pnpm", "dev"]
```

This approach avoids static generation issues and is more forgiving with client-side hooks like `useSearchParams`, but comes with some performance trade-offs.

***REMOVED******REMOVED*** Development

***REMOVED******REMOVED******REMOVED*** Prerequisites

- Node.js 20+
- pnpm 10.10.0+

***REMOVED******REMOVED******REMOVED*** Setup

```bash
***REMOVED*** Install dependencies
pnpm install

***REMOVED*** Start development server
pnpm dev
```

***REMOVED******REMOVED*** Building for Production

```bash
***REMOVED*** Build the application
pnpm production-build

***REMOVED*** Start the production server
pnpm start
```
