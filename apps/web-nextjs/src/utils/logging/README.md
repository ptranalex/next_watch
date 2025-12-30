# Logging Utilities

This directory contains utilities for logging in the application.

## Files

- `loggerConfig.ts` - Main logging utility with multiple log levels and features
- `examples/` - Example implementations of the logging utilities

## Usage

```typescript
import { createLogger, loggerConfig, LogLevel } from "@/utils/logging";

// Create a logger with automatic group detection
const logger = createLogger();

// Or with explicit group name
const logger = createLogger("ComponentName");

// Basic logging
logger.debug("Debug message", { data: "value" });
logger.info("Information message");
logger.warn("Warning message");
logger.error("Error message", new Error("Something went wrong"));

// Log once (useful in components)
logger.debugOnce("This appears only once even if component re-renders");

// Configuration
loggerConfig.setMinLevel(LogLevel.WARN); // Only show warnings and errors
loggerConfig.disableGroup("GroupName"); // Disable logs for a specific group
```

See the [loggerConfig.md](./loggerConfig.md) file for complete documentation.
