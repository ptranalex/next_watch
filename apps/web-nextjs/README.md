# NextWatch Web Application

A modern movie tracking web application built with Next.js, TypeScript, and Chakra UI.

## 📋 Overview

NextWatch Web is the frontend application for the NextWatch platform, allowing users to:

- Discover and search for movies
- Track watched, liked, and watchlist movies
- View movie details, trailers, and cast information
- Manage user profiles and preferences
- Enjoy a mobile-optimized experience with touch-friendly interfaces
- Filter and sort movies by various criteria
- Receive personalized recommendations

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- pnpm 10+
- Access to the NextWatch backend API (or mock data)

### Installation

```bash
# Navigate to the web app directory
cd apps/web-nextjs

# Install dependencies with pnpm
pnpm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local to configure your environment

# Start development server
pnpm dev
```

### Docker Deployment

The application includes a Docker configuration for containerized deployment:

```bash
# Build Docker image
docker build -t web-nextjs -f apps/web-nextjs/Dockerfile .

# Run Docker container
docker run -d -p 3000:3000 --name web-nextjs-app web-nextjs
```

#### Docker Architecture

The Docker setup uses a specially configured development mode that:

- Avoids static generation issues with Next.js in production mode
- Correctly handles React hooks like useSearchParams with proper Suspense boundaries
- Provides a secure environment with non-root users
- Reduces container size through careful layer management

#### Docker Environment Variables

- `NODE_ENV=development` - Uses development mode for best compatibility
- `NEXT_TELEMETRY_DISABLED=1` - Disables Next.js telemetry
- `PORT=3000` - Sets the internal container port
- `NEXT_PUBLIC_API_URL` - URL of the NextWatch backend API
- `NEXT_PUBLIC_TMDB_IMAGE_BASE_URL` - Base URL for TMDB images
- `NEXT_PUBLIC_ENABLE_ANALYTICS` - Toggle analytics (true/false)

### Available Scripts

- `pnpm dev` - Start the development server
- `pnpm build` - Build for production
- `pnpm start` - Run the production build
- `pnpm lint` - Run ESLint
- `pnpm test` - Run unit tests
- `pnpm test:e2e` - Run end-to-end tests with Cypress
- `pnpm storybook` - Start Storybook for component development
- `pnpm docker-build` - Custom build script optimized for Docker deployment

## 🏗️ Architecture

NextWatch follows **Clean Architecture** principles with a domain-driven approach:

```
src/
├── app/                # Next.js App Router pages and layouts
├── components/         # React components
│   ├── mobile/         # Mobile-specific components
│   │   ├── common/     # Shared mobile UI components
│   │   ├── filters/    # Mobile filter components
│   │   └── layout/     # Mobile layout components
│   ├── common/         # Shared components
│   ├── layout/         # Layout components
│   └── features/       # Feature-specific components
├── context/            # React context providers
│   └── ResponsiveContext.tsx  # Responsive design context
├── domain/             # Domain entities and business logic
│   ├── entities/       # Core data structures and type definitions
│   └── models/         # Business models
├── hooks/              # React hooks
│   ├── core/           # App-wide hooks (auth, etc.)
│   ├── domain/         # Domain-specific hooks
│   └── ui/             # UI utility hooks
├── services/           # External services integration
│   ├── api/            # API client implementations
│   └── storage/        # Local storage utilities
├── store/              # Global state management
│   ├── slices/         # State slices
│   └── middleware/     # Redux middleware
└── utils/              # Utility functions
    ├── formatting/     # Date and text formatting
    ├── validation/     # Form validation
    └── analytics/      # Analytics utilities
```

### Key Architectural Concepts

1. **Domain Layer** - Core business entities independent of UI/framework
2. **Hooks Layer** - React-specific integration with domain logic
3. **Services Layer** - External API communication
4. **Components** - UI presentation logic

### Mobile-First Design

NextWatch implements a mobile-first approach with these key features:

1. **Responsive Context Provider** - Centralizes device detection and breakpoint logic
2. **Touch-Optimized Components** - Designed specifically for mobile interfaces:

   - Bottom Sheets instead of modals
   - Bottom Action Bars for thumb-reachable interfaces
   - Pull-to-refresh with haptic feedback
   - Swipe actions for list items
   - Optimized touch targets (44×44px minimum)

3. **Adaptive Layout System**:

   - Components that automatically adapt to screen size
   - Conditional rendering based on device capabilities
   - Proper spacing for touch interactions

4. **Performance Optimizations**:
   - Skeleton loading screens for perceived performance
   - Lazy-loaded modal content
   - Touch event optimization
   - Image optimization with Next.js Image component
   - Code splitting for faster initial load

### Mobile-First Development Guidelines

When adding new features or components to NextWatch, follow these guidelines:

1. **Start with Mobile Design First**

   - Begin by designing and implementing the mobile version of the UI
   - Use the existing mobile components in `src/components/mobile/*`
   - Focus on simple, focused UI with essential features only

2. **Touch-Friendly Interactions**

   - Ensure all interactive elements are at least 44×44px (Apple HIG guideline)
   - Place primary actions within easy thumb reach (bottom of screen)
   - Use SwipeAction for list item interactions
   - Implement haptic feedback for important interactions using `window.navigator.vibrate()`

3. **Component Organization**

   - Place mobile-specific components in `src/components/mobile/`
   - Common mobile patterns go in `src/components/mobile/common/`
   - Use naming convention `Mobile*` for mobile-specific components

4. **Responsive Enhancement**

   - After completing mobile implementation, enhance for larger screens
   - Use Chakra UI's responsive object syntax: `prop={{ base: "mobileValue", md: "desktopValue" }}`
   - Hide/show elements with Chakra's `Show` component or `display={{ base: "none", md: "block" }}`

5. **Performance Considerations**

   - Implement skeleton loaders for mobile (see `src/components/mobile/loaders/`)
   - Use dynamic imports with `next/dynamic` for non-critical components
   - Test on actual mobile devices or throttled connections

6. **Testing Your Mobile Implementation**

   - Use Chrome DevTools' device emulation
   - Test touch interactions on real devices when possible
   - Verify performance on low-end mobile devices

7. **Navigation Patterns**

   - Use the `MobileNavBar` component for primary navigation
   - Implement the `BottomSheet` component instead of traditional modals
   - Consider gesture-based navigation where appropriate

8. **Code Splitting Strategy**
   - Separate mobile/desktop logic when significant differences exist
   - Use responsive props for minor differences
   - Create container components that choose between implementations based on screen size

### Existing Mobile Components

| Component       | Purpose                                   | Usage                                                                        |
| --------------- | ----------------------------------------- | ---------------------------------------------------------------------------- |
| BottomSheet     | Mobile alternative to modals              | `<BottomSheet isOpen={isOpen} onClose={close}>{content}</BottomSheet>`       |
| BottomActionBar | Fixed action bar at bottom of screen      | `<BottomActionBar actions={[...]}/>`                                         |
| MobileNavBar    | Bottom navigation tabs                    | Added automatically to AppShell                                              |
| PullToRefresh   | Add pull-to-refresh to scrollable content | `<PullToRefresh onRefresh={loadData}>{content}</PullToRefresh>`              |
| SwipeAction     | Add swipe gestures to list items          | `<SwipeAction leftActions={[...]} rightActions={[...]}>{item}</SwipeAction>` |
| MovieSkeleton   | Skeleton loader for movie items           | `<MovieSkeleton count={8} isGrid={false} />`                                 |

## 📚 Documentation Structure

The codebase includes detailed documentation organized by feature area:

- `/src/domain/README.md` - Domain layer architecture and usage
- `/src/hooks/README.md` - React hooks organization and best practices
- `/src/services/README.md` - API services documentation

## 🔄 Data Flow

1. **Components** use **Hooks** to interact with data
2. **Hooks** use **Services** to fetch data from APIs
3. **Services** transform API responses into **Domain Entities**
4. **Components** render UI based on Domain Entities

## 🧪 Testing

The application uses a comprehensive testing strategy:

- **Unit Tests**: Test individual components and hooks using React Testing Library and Jest
- **Integration Tests**: Test interactions between components
- **End-to-End Tests**: Test complete user flows with Cypress

To run tests:

```bash
# Run unit and integration tests
pnpm test

# Run e2e tests
pnpm test:e2e

# Run with coverage report
pnpm test:coverage
```

## 🖥️ Browser Support

The application supports:

- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)
- iOS Safari (latest 2 versions)
- Android Chrome (latest 2 versions)

## 📱 Progressive Web App (PWA)

NextWatch can be installed as a PWA on supported devices, providing:

- Offline capability for core features
- Home screen installation
- Native-like experience

## 🔒 Authentication

Authentication is handled using:

- JSON Web Tokens (JWT)
- Secure HTTP-only cookies
- Protected routes with middleware
- Session persistence across page refreshes

## 🌐 Internationalization

The application supports multiple languages through:

- React-intl for message formatting
- Language detection and selection
- RTL layout support for appropriate languages

## 🛡️ Security Measures

- CSRF protection
- Content Security Policy
- XSS prevention
- Input validation
- Rate limiting
- HTTPS only

## 👥 Contributing

Please see the [Contributing Guide](../CONTRIBUTING.md) for details on how to contribute to this project.

## 📝 License

MIT

## URL Parameter Handling

The application uses a custom hook called `useUrlParams` for handling URL parameters safely in both server and client components. This approach solves the common SSR/hydration issues with `useSearchParams` in Next.js.

### Using the `useUrlParams` hook

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

### Benefits of this approach

1. **Type safety**: Parameters are properly typed
2. **Server-side rendering compatible**: Works in both SSR and client environments
3. **No hydration errors**: Handles the hydration process correctly
4. **No suspense boundaries needed**: Eliminates the need for wrapping components in suspense boundaries
5. **Production build compatible**: Works correctly in production builds without special accommodations

## Sustainable Docker Strategy

For the most sustainable Docker deployment, we have two main approaches:

### Approach 1: Production Build with useUrlParams

Use our custom `useUrlParams` hook throughout the codebase, which safely handles URL parameters without requiring Suspense boundaries. This approach works with proper static generation and can use a standard production Dockerfile.

### Approach 2: Development Server Mode for Production

In some cases where you can't update all component instances, running in development mode can provide a more flexible solution:

```dockerfile
# Simplified Dockerfile for Next.js
FROM node:20-alpine

# Setup app directory
WORKDIR /app

# Install dependencies
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm install --frozen-lockfile

# Copy application code
COPY . .

# Configure for development mode
ENV NODE_ENV=development
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000

# Start the development server
CMD ["pnpm", "dev"]
```

This approach avoids static generation issues and is more forgiving with client-side hooks like `useSearchParams`, but comes with some performance trade-offs.

## Development

### Prerequisites

- Node.js 20+
- pnpm 10.10.0+

### Setup

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev
```

## Building for Production

```bash
# Build the application
pnpm production-build

# Start the production server
pnpm start

dummy
```

## URL-Based Filter System

The application uses URL-based state management for filters instead of React context. This provides several benefits:

- Filter state persists across page refreshes
- Filters can be shared via URL
- Browser navigation (back/forward) works with filter changes
- Improved SEO as filters are reflected in URLs

### Available URL Parameters

The following URL parameters can be used for filtering:

| Parameter              | Type   | Description                            | Example                      |
| ---------------------- | ------ | -------------------------------------- | ---------------------------- |
| q                      | string | Search query                           | `?q=matrix`                  |
| genre                  | string | Movie genre                            | `?genre=action`              |
| rating_imdb            | number | Minimum IMDb rating (0-10)             | `?rating_imdb=7.5`           |
| rating_rotten_tomatoes | number | Minimum Rotten Tomatoes rating (0-100) | `?rating_rotten_tomatoes=80` |
| rating_metacritic      | number | Minimum Metacritic rating (0-100)      | `?rating_metacritic=70`      |
| year                   | number | Release year                           | `?year=2023`                 |
| sort                   | string | Sort field                             | `?sort=release_date`         |
| order                  | string | Sort order (asc/desc)                  | `?order=desc`                |

### Examples

- View all action movies: `/movies?genre=action`
- 2023 movies with IMDb rating 7+: `/movies?year=2023&rating_imdb=7`
- Highly rated comedies sorted by rating: `/movies?genre=comedy&rating_imdb=8&sort=imdb_rating&order=desc`

## Components

The filter system is composed of several components:

- `MovieFilter`: Rating and year sliders
- `GenreSelector`: Genre selection buttons
- `SortSelector`: Sort type and direction controls
- `SearchInput`: Movie title search field

## Mobile Development Guidelines

When working on mobile features:

1. **Always test on real devices** - Simulators don't always accurately represent touch behavior
2. **Focus on motion efficiency** - Minimize the number of taps and user effort
3. **Optimize for offline and poor connectivity** - Mobile networks can be unreliable
4. **Use haptic feedback appropriately** - Provide tactile confirmation for key actions
5. **Consider mobile-specific interaction patterns** - Don't just shrink desktop UI

### Mobile Component Structure

Mobile-specific components are organized in the `components/mobile` directory:

- `common/` - Reusable mobile UI patterns (BottomSheet, BottomActionBar, etc.)
- `filters/` - Filter interfaces optimized for mobile
- `layout/` - Mobile layout components

### Responsive Integration

Use the `useResponsive()` hook to access device information:

```tsx
import { useResponsive } from "@/context/ResponsiveContext";

function MyComponent() {
  const { isMobile, isTablet, isDesktop, hasTouchScreen } = useResponsive();

  // Conditional rendering based on device
  return isMobile ? <MobileView /> : <DesktopView />;
}
```
