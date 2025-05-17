***REMOVED*** Utility Functions

This directory contains reusable utility functions that provide common functionality across the application.

***REMOVED******REMOVED*** 📂 Current Directory Structure

```
utils/
├── logging/             ***REMOVED*** Logging utilities
│   ├── loggerConfig.ts  ***REMOVED*** Core logging utility
│   ├── loggerConfig.md  ***REMOVED*** Documentation for logger
│   ├── README.md        ***REMOVED*** Logging utilities overview
│   ├── index.ts         ***REMOVED*** Exports from logging
│   └── examples/        ***REMOVED*** Logger usage examples
│       └── loggerConfigExample.tsx
├── auth/                ***REMOVED*** Authentication utilities
│   ├── authTokenManager.ts ***REMOVED*** Auth token management
│   └── index.ts         ***REMOVED*** Exports from auth
├── media/               ***REMOVED*** Media-related utilities
│   ├── image-urls.ts    ***REMOVED*** Image URL handling
│   └── index.ts         ***REMOVED*** Exports from media
└── index.ts             ***REMOVED*** Main export for all utilities
```

***REMOVED******REMOVED*** 🛠️ Ideal Utility Categories

For future development, consider these additional categories:

```
utils/
├── date/               ***REMOVED*** Date manipulation utilities
│   ├── formatters.ts   ***REMOVED*** Date formatting utilities
│   └── parsers.ts      ***REMOVED*** Date parsing utilities
├── string/             ***REMOVED*** String manipulation utilities
│   ├── formatters.ts   ***REMOVED*** String formatting utilities
│   └── validators.ts   ***REMOVED*** String validation utilities
├── array/              ***REMOVED*** Array manipulation utilities
│   └── transformers.ts ***REMOVED*** Array transformation utilities
├── number/             ***REMOVED*** Number manipulation utilities
│   └── formatters.ts   ***REMOVED*** Number formatting utilities
├── api/                ***REMOVED*** API-related utilities
│   └── error-handler.ts ***REMOVED*** API error handling utilities
└── storage/            ***REMOVED*** Storage-related utilities
    ├── local-storage.ts ***REMOVED*** LocalStorage utilities
    └── session-storage.ts ***REMOVED*** SessionStorage utilities
```

***REMOVED******REMOVED*** 🔄 Usage Pattern

Import utility functions directly from their modules:

```typescript
import { createLogger } from "@/utils/logging";
import { getAuthToken } from "@/utils/auth";
import { getImageUrl } from "@/utils/media";

// Use in components
const logger = createLogger("MyComponent");
const token = getAuthToken();
const imageUrl = getImageUrl(movie.poster_path);
```

Or use the centralized export:

```typescript
import { createLogger, getAuthToken, getImageUrl } from "@/utils";

// Use in components
const logger = createLogger("MyComponent");
```

***REMOVED******REMOVED*** 📝 Utility Development Guidelines

When creating utility functions:

1. **Pure Functions**: Utilities should be pure functions without side effects
2. **Single Responsibility**: Each function should do one thing well
3. **TypeScript Types**: Include proper TypeScript typing for parameters and return values
4. **Documentation**: Add JSDoc comments for all functions
5. **Testing**: Write unit tests for each utility function
6. **Categorization**: Place utilities in the appropriate category

***REMOVED******REMOVED******REMOVED*** Example Pattern

```typescript
/**
 * Formats a number as a rating (e.g., "4.5/10")
 *
 * @param {number} rating - The rating value
 * @param {number} maxRating - The maximum possible rating
 * @param {number} decimals - Number of decimal places to show
 * @returns {string} Formatted rating string
 */
export function formatRating(
  rating: number,
  maxRating: number = 10,
  decimals: number = 1
): string {
  if (isNaN(rating)) return "N/A";
  return `${rating.toFixed(decimals)}/${maxRating}`;
}
```

***REMOVED******REMOVED*** 🧪 Testing Utilities

Utility functions should be thoroughly tested:

```typescript
import { formatRating } from "./formatters";

describe("formatRating", () => {
  it("formats rating with default parameters", () => {
    expect(formatRating(7.5)).toBe("7.5/10");
  });

  it("handles custom max rating", () => {
    expect(formatRating(3.5, 5)).toBe("3.5/5");
  });

  it("handles custom decimal places", () => {
    expect(formatRating(7.567, 10, 2)).toBe("7.57/10");
  });

  it("handles NaN values", () => {
    expect(formatRating(NaN)).toBe("N/A");
  });
});
```

***REMOVED******REMOVED*** 📚 Related Documentation

- [JavaScript MDN Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
