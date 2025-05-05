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

***REMOVED******REMOVED******REMOVED*** Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build for production
- `npm start` - Run the production build
- `npm run lint` - Run ESLint

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
