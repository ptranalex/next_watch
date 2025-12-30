# Utility Functions

This directory contains reusable utility functions that provide common functionality across the application.

## 📂 Current Directory Structure

```
utils/
├── logging/             # Logging utilities
│   ├── loggerConfig.ts  # Core logging utility
│   ├── loggerConfig.md  # Documentation for logger
│   ├── README.md        # Logging utilities overview
│   ├── index.ts         # Exports from logging
│   └── examples/        # Logger usage examples
│       └── loggerConfigExample.tsx
├── auth/                # Authentication utilities
│   ├── authTokenManager.ts # Auth token management
│   └── index.ts         # Exports from auth
├── media/               # Media-related utilities
│   ├── image-urls.ts    # Image URL handling
│   └── index.ts         # Exports from media
└── index.ts             # Main export for all utilities
```

## 🛠️ Ideal Utility Categories

For future development, consider these additional categories:

```
utils/
├── date/               # Date manipulation utilities
│   ├── formatters.ts   # Date formatting utilities
│   └── parsers.ts      # Date parsing utilities
├── string/             # String manipulation utilities
│   ├── formatters.ts   # String formatting utilities
│   └── validators.ts   # String validation utilities
├── array/              # Array manipulation utilities
│   └── transformers.ts # Array transformation utilities
├── number/             # Number manipulation utilities
│   └── formatters.ts   # Number formatting utilities
├── api/                # API-related utilities
│   └── error-handler.ts # API error handling utilities
└── storage/            # Storage-related utilities
    ├── local-storage.ts # LocalStorage utilities
    └── session-storage.ts # SessionStorage utilities
```

## 🔄 Usage Pattern

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

## 📝 Utility Development Guidelines

When creating utility functions:

1. **Pure Functions**: Utilities should be pure functions without side effects
2. **Single Responsibility**: Each function should do one thing well
3. **TypeScript Types**: Include proper TypeScript typing for parameters and return values
4. **Documentation**: Add JSDoc comments for all functions
5. **Testing**: Write unit tests for each utility function
6. **Categorization**: Place utilities in the appropriate category

### Example Pattern

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

## 🧪 Testing Utilities

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

## 📚 Related Documentation

- [JavaScript MDN Docs](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
