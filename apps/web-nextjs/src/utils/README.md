***REMOVED*** Utility Functions

This directory contains reusable utility functions that provide common functionality across the application.

***REMOVED******REMOVED*** 📂 Directory Structure

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
├── storage/            ***REMOVED*** Storage-related utilities
│   ├── local-storage.ts ***REMOVED*** LocalStorage utilities
│   └── session-storage.ts ***REMOVED*** SessionStorage utilities
└── index.ts            ***REMOVED*** Main export for utilities
```

***REMOVED******REMOVED*** 🛠️ Utility Categories

***REMOVED******REMOVED******REMOVED*** Date Utilities

Functions for working with dates:

```typescript
// utils/date/formatters.ts
export function formatDate(
  date: Date | string,
  format: string = "YYYY-MM-DD"
): string {
  // Format implementation...
}

export function relativeTime(date: Date | string): string {
  // Relative time implementation (e.g., "2 hours ago")...
}

// utils/date/parsers.ts
export function parseDate(dateString: string, format?: string): Date {
  // Parse implementation...
}
```

***REMOVED******REMOVED******REMOVED*** String Utilities

Functions for string manipulation:

```typescript
// utils/string/formatters.ts
export function capitalize(str: string): string {
  if (!str) return "";
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export function truncate(str: string, maxLength: number): string {
  if (!str || str.length <= maxLength) return str;
  return str.slice(0, maxLength) + "...";
}

// utils/string/validators.ts
export function isValidEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}
```

***REMOVED******REMOVED******REMOVED*** Array Utilities

Functions for array operations:

```typescript
// utils/array/transformers.ts
export function groupBy<T>(array: T[], key: keyof T): Record<string, T[]> {
  return array.reduce((result, item) => {
    const groupKey = String(item[key]);
    result[groupKey] = result[groupKey] || [];
    result[groupKey].push(item);
    return result;
  }, {} as Record<string, T[]>);
}

export function uniqueBy<T>(array: T[], key: keyof T): T[] {
  const seen = new Set();
  return array.filter((item) => {
    const value = item[key];
    if (seen.has(value)) return false;
    seen.add(value);
    return true;
  });
}
```

***REMOVED******REMOVED******REMOVED*** Number Utilities

Functions for number formatting:

```typescript
// utils/number/formatters.ts
export function formatCurrency(
  value: number,
  currency: string = "USD"
): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
  }).format(value);
}

export function formatPercentage(value: number, decimals: number = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}
```

***REMOVED******REMOVED******REMOVED*** API Utilities

Functions for API operations:

```typescript
// utils/api/error-handler.ts
import {
  APIError,
  NetworkError,
  ValidationError,
} from "@/services/api/core/errors";

export function handleApiError(error: unknown): {
  message: string;
  code?: string;
} {
  if (error instanceof NetworkError) {
    return {
      message: "Network error. Please check your connection.",
      code: "NETWORK_ERROR",
    };
  }

  if (error instanceof ValidationError) {
    return {
      message: "Validation error. Please check your inputs.",
      code: "VALIDATION_ERROR",
    };
  }

  if (error instanceof APIError) {
    return { message: error.message, code: String(error.statusCode) };
  }

  return { message: "An unexpected error occurred.", code: "UNKNOWN_ERROR" };
}
```

***REMOVED******REMOVED******REMOVED*** Storage Utilities

Functions for browser storage:

```typescript
// utils/storage/local-storage.ts
export function getItem<T>(key: string, defaultValue?: T): T | undefined {
  if (typeof window === "undefined") return defaultValue;

  const item = localStorage.getItem(key);
  if (!item) return defaultValue;

  try {
    return JSON.parse(item) as T;
  } catch {
    return defaultValue;
  }
}

export function setItem<T>(key: string, value: T): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(key, JSON.stringify(value));
}
```

***REMOVED******REMOVED*** 🔄 Usage Pattern

Import utility functions directly from their modules:

```typescript
import { formatDate, relativeTime } from "@/utils/date/formatters";
import { capitalize, truncate } from "@/utils/string/formatters";

// Use in components
const formattedDate = formatDate(movie.release_date);
const title = capitalize(movie.title);
const description = truncate(movie.overview, 150);
```

Or use the centralized export:

```typescript
import { formatDate, capitalize, truncate } from "@/utils";

// Use in components
const formattedDate = formatDate(movie.release_date);
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
