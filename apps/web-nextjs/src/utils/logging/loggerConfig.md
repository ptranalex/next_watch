# loggerConfig Utility

A powerful and lightweight development logging utility for Next.js applications.

## Features

- 📊 **Log Levels**: Supports DEBUG, INFO, WARN, and ERROR log levels
- 🏠 **Environment Aware**: Only enabled in development mode by default
- 🔍 **Namespaced Logging**: Group logs by component or feature
- 🎨 **Colorized Output**: Visual distinction for different log levels
- 🔇 **Selective Silencing**: Disable specific log groups when needed
- 🧩 **Typed API**: Full TypeScript support
- 🔄 **Log Once**: Prevent duplicate logs in render loops
- 🔍 **Auto-Group**: Automatically detect caller module
- 😊 **Emoji Prefixes**: Visual indicators for log levels

## Basic Usage

```tsx
import { createLogger } from "@/utils/logging";

// With explicit group name
const logger = createLogger("MovieComponent");

// Or with auto-detected group name
const logger = createLogger();

// In your component
function MovieComponent({ id, title }) {
  // Regular logging
  logger.debug("Component mounted", { id, title }); // 🐛 [DEBUG] [MovieComponent]

  // Only logs once, even if component re-renders
  logger.warnOnce("Potential performance issue"); // ⚠️ [WARN] [MovieComponent]

  if (!title) {
    logger.warn("Movie missing title");
  }

  return <div>{title}</div>;
}
```

## Pre-configured Loggers

For common application areas, you can use pre-configured loggers:

```tsx
import {
  appLogger,
  apiLogger,
  storeLogger,
  routeLogger,
} from "@/utils/logging";

// Use them directly
appLogger.info("Application initialized");
apiLogger.error("API request failed", error);
storeLogger.debug("State updated", newState);
routeLogger.info("Navigated to", path);
```

## Configuration

You can customize the logging behavior globally:

```tsx
import { loggerConfig, LogLevel } from "@/utils/logging";

// Disable all logs
loggerConfig.setEnabled(false);

// Only show warnings and errors
loggerConfig.setMinLevel(LogLevel.WARN);

// Disable logs from specific groups
loggerConfig.disableGroup("MovieList");
loggerConfig.disableGroup("AuthForm");

// Re-enable logs for a group
loggerConfig.enableGroup("MovieList");

// Toggle emoji prefixes
loggerConfig.setUseEmoji(false); // Turn off emoji prefixes

// Clear the "once" log memory
loggerConfig.clearLoggedMessages();

// Reset to defaults
loggerConfig.reset();
```

## Production Setup

In `_app.tsx` or similar initialization file:

```tsx
import { setupProductionLogging } from "@/utils/logging";

// This will automatically disable logs in production
setupProductionLogging();
```

## Advanced Usage

### Using "Once" Methods to Prevent Duplicate Logs

```tsx
function Component() {
  // These will only log once, no matter how many times the component re-renders
  logger.debugOnce("This debug message appears only once");
  logger.infoOnce("This info appears only once");
  logger.warnOnce("This warning appears only once");
  logger.errorOnce("This error appears only once");

  return <div>Component Content</div>;
}
```

### Conditional Rendering Based on Logging State

```tsx
import { createLogger } from "@/utils/logging";

const logger = createLogger("DebugPanel");

function DebugPanel() {
  // Only render debug UI if logging is enabled for this component
  if (!logger.isEnabled()) return null;

  return (
    <div className="debug-panel">
      <h3>Debug Information</h3>
      {/* Debug content */}
    </div>
  );
}
```

### Object Logging

The logger supports passing objects for inspection:

```tsx
logger.info("User data:", {
  id: 123,
  name: "Alex",
  permissions: ["read", "write"],
});
```

## Best Practices

1. **Use namespaced loggers**: Create a logger per component or logical module
2. **Let auto-grouping work for you**: When no group name is provided, the logger will automatically use the calling file or function name
3. **Use log-once in components**: For warnings and errors in frequently re-rendered components, use the \*Once methods
4. **Choose appropriate log levels**:
   - `debug`: Detailed information for development
   - `info`: General application flow events
   - `warn`: Potential issues that don't break functionality
   - `error`: Critical problems that affect functionality
5. **Clean up before production**: Ensure logs don't affect performance
6. **Structured data**: Pass objects as separate arguments rather than string concatenation
