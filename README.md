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
└── tools/               ***REMOVED*** Various tools and scripts
```

***REMOVED******REMOVED*** Features

- Movie tracking (watched, liked, watchlist)
- User authentication and profiles
- Movie recommendations based on user preferences
- Movie search and discovery
- Responsive design for mobile and desktop

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
- Node.js 16+
- PostgreSQL 13+

***REMOVED******REMOVED******REMOVED*** Setup

1. Clone the repository
2. Install dependencies:
   ```
   cd apps/backend-api
   pip install -e .
   cd ../../apps/web-nextjs
   npm install
   ```
3. Configure environment:
   Copy `.env.example` to `.env` in each app directory and update settings

***REMOVED******REMOVED******REMOVED*** Running the Applications

**Backend:**

```
cd apps/backend-api
python -m src.backend_api.main
```

**Frontend:**

```
cd apps/web-nextjs
npm run dev
```

***REMOVED******REMOVED*** API Documentation

Once the backend is running, access the Swagger documentation at:
`http://localhost:8000/docs`

***REMOVED******REMOVED*** Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on contributing to this project.
