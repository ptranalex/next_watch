***REMOVED*** NextWatch

A modern movie tracking application built with Next.js and Python.

***REMOVED******REMOVED*** Project Structure

This is a monorepo containing multiple packages:

```
next_watch/
├── apps/
│   ├── backend-api/     ***REMOVED*** Python FastAPI backend
│   ├── data-importer/   ***REMOVED*** Data import utilities
│   ├── mobile-flutter/  ***REMOVED*** Mobile application
│   └── web-nextjs/      ***REMOVED*** Next.js web application
├── libs/
│   └── movie-storage/   ***REMOVED*** Shared Python library for movie data models
└── scripts/             ***REMOVED*** Various tools and scripts
```

***REMOVED******REMOVED*** Features

- Movie tracking (watched, liked, watchlist)
- User authentication and profiles
- Movie recommendations based on user preferences
- Movie search and discovery
- Responsive design for mobile and desktop
- Mobile-first approach with touch-friendly interfaces

***REMOVED******REMOVED*** Backend Architecture

The backend follows a Command Query Responsibility Segregation (CQRS) pattern:

- **Commands (Services)**: Handle state-changing operations (create, update, delete)
- **Queries**: Handle optimized read operations

This separation allows for specialized optimization of read and write paths.

***REMOVED******REMOVED******REMOVED*** Key Components

- **Routes**: API endpoints for client interaction
- **Services**: Business logic for state-changing operations
- **Queries**: Optimized read operations
- **Models**: Data structures with SQLModel
- **Schemas**: Pydantic models for request/response validation

***REMOVED******REMOVED*** Getting Started

***REMOVED******REMOVED******REMOVED*** Prerequisites

- Python 3.10+
- Node.js 18+
- pnpm 10+
- PostgreSQL 13+

***REMOVED******REMOVED******REMOVED*** Setup

1. Clone the repository
2. Install dependencies:

   **For Python components:**

   ```
   cd apps/backend-api
   pip install -e .
   ```

   **For JavaScript/TypeScript components (using pnpm):**

   ```
   ***REMOVED*** Install pnpm if not already installed
   npm install -g pnpm

   ***REMOVED*** Install dependencies for all JS/TS packages
   pnpm install
   ```

3. Configure environment:
   Copy `.env.example` to `.env` in each app directory and update settings

***REMOVED******REMOVED******REMOVED*** Running the Applications

**Backend API:**

```
cd apps/backend-api
***REMOVED*** Using the CLI (recommended):
poetry run backend-api server start

***REMOVED*** Or with explicit options:
poetry run backend-api server start --port 8080 --log-level DEBUG
```

**Web Frontend:**

```
***REMOVED*** From repository root
pnpm dev:web

***REMOVED*** Or from the web-nextjs directory
cd apps/web-nextjs
pnpm dev
```

**Data Importer:**

```
cd apps/data-importer
***REMOVED*** Sync movies by year range
data-importer sync movies 2022 2023 --credits --save

***REMOVED*** Or run in interactive shell mode
data-importer shell
```

***REMOVED******REMOVED******REMOVED*** Building the Applications

**Frontend:**

```
***REMOVED*** From repository root
pnpm build:web

***REMOVED*** Or from the web-nextjs directory
cd apps/web-nextjs
pnpm build
```

***REMOVED******REMOVED*** API Documentation

Once the backend is running, access the Swagger documentation at:
`http://localhost:8000/docs`

***REMOVED******REMOVED*** Documentation Structure

Each package contains its own README with detailed information:

- [Backend API Documentation](./apps/backend-api/README.md)
- [Web App Documentation](./apps/web-nextjs/README.md)
- [Data Importer Documentation](./apps/data-importer/README.md)
- [Movie Storage Documentation](./libs/movie-storage/README.md)

***REMOVED******REMOVED*** Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on contributing to this project.
