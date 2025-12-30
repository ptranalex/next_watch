/**
 * loggerConfig - A configurable development logging utility
 *
 * Features:
 * - Different log levels (debug, info, warn, error)
 * - Environment-based toggling (only logs in development)
 * - Group/namespace support with auto-detection
 * - Log-once functionality to prevent duplicates
 * - Visual formatting with colors and emoji
 * - Selective enable/disable for specific log groups
 */

// Log levels with numeric values for filtering
export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  NONE = 999, // For completely disabling logs
}

// Colors for different log levels
const LOG_COLORS: Record<LogLevel, string> = {
  [LogLevel.DEBUG]: '#9e9e9e', // Gray
  [LogLevel.INFO]: '#2196f3', // Blue
  [LogLevel.WARN]: '#ff9800', // Orange
  [LogLevel.ERROR]: '#f44336', // Red
  [LogLevel.NONE]: '#000000', // Black, though should never be used
}

// Log level names for display
const LOG_NAMES: Record<LogLevel, string> = {
  [LogLevel.DEBUG]: 'DEBUG',
  [LogLevel.INFO]: 'INFO',
  [LogLevel.WARN]: 'WARN',
  [LogLevel.ERROR]: 'ERROR',
  [LogLevel.NONE]: 'NONE',
}

// Emoji symbols for different log levels
const LOG_SYMBOLS: Record<LogLevel, string> = {
  [LogLevel.DEBUG]: '🐛',
  [LogLevel.INFO]: 'ℹ️',
  [LogLevel.WARN]: '⚠️',
  [LogLevel.ERROR]: '❌',
  [LogLevel.NONE]: '',
}

// Global configuration
interface DevLogConfig {
  enabled: boolean
  minLevel: LogLevel
  disabledGroups: Set<string>
  useEmoji: boolean // Whether to show emoji symbols in logs
}

// Default configuration
const config: DevLogConfig = {
  // Only enable in development and when not server-side rendering
  enabled: typeof window !== 'undefined' && process.env.NODE_ENV === 'development',
  minLevel: LogLevel.DEBUG,
  disabledGroups: new Set<string>(),
  useEmoji: true, // Enable emoji symbols by default
}

// Track messages that have already been logged (for "once" methods)
// Using a Map of group -> level -> Set of messages
const loggedMessages: Map<string, Map<LogLevel, Set<string>>> = new Map()

/**
 * Automatically determine the caller module from the stack trace
 * @returns The name of the calling module/file
 */
const autoGroup = (): string => {
  try {
    const err = new Error()
    const stackLine = err.stack?.split('\n')[3] // skip 0=Error, 1=autoGroup(), 2=createLogger, 3=caller

    if (!stackLine) return 'unknown'

    // Try to extract the function or file name
    // First try to match "at FunctionName "
    const functionMatch = stackLine.match(/at\s+([\w.]+)\s+\(/)?.[1]
    if (functionMatch) return functionMatch

    // Otherwise, try to extract the file path and get the file name
    const fileMatch = stackLine.match(/\(([^)]+)\)/)?.[1]
    if (fileMatch) {
      // Try to get just the file name without extension
      const fileName = fileMatch.split('/').pop()?.split('.')[0]
      return fileName || 'unknown'
    }

    return 'unknown'
  } catch {
    return 'unknown'
  }
}

/**
 * Check if a message has already been logged for a specific group and level
 */
const hasLoggedBefore = (group: string, level: LogLevel, message: string): boolean => {
  const groupMessages = loggedMessages.get(group)
  if (!groupMessages) return false

  const levelMessages = groupMessages.get(level)
  if (!levelMessages) return false

  return levelMessages.has(message)
}

/**
 * Mark a message as having been logged for a specific group and level
 */
const markAsLogged = (group: string, level: LogLevel, message: string): void => {
  // Get or create group map
  let groupMessages = loggedMessages.get(group)
  if (!groupMessages) {
    groupMessages = new Map()
    loggedMessages.set(group, groupMessages)
  }

  // Get or create level set
  let levelMessages = groupMessages.get(level)
  if (!levelMessages) {
    levelMessages = new Set()
    groupMessages.set(level, levelMessages)
  }

  // Add message to set
  levelMessages.add(message)
}

/**
 * Main logging function
 */
function log(level: LogLevel, group: string, message: string, ...args: unknown[]): void {
  // Skip if logging is disabled, level is below minimum, or group is disabled
  if (!config.enabled || level < config.minLevel || config.disabledGroups.has(group)) {
    return
  }

  const color = LOG_COLORS[level]
  const levelName = LOG_NAMES[level]
  const symbol = config.useEmoji ? LOG_SYMBOLS[level] : ''

  // Format: [LEVEL] [group] message
  const formattedMessage = `%c${symbol} [${levelName}]%c [${group}] ${message}`

  // Prepare styles
  const levelStyle = `color: ${color}; font-weight: bold;`
  const messageStyle = '' // Reset to default

  // Select appropriate console method based on level
  let method: 'log' | 'info' | 'warn' | 'error' = 'log'
  switch (level) {
    case LogLevel.INFO:
      method = 'info'
      break
    case LogLevel.WARN:
      method = 'warn'
      break
    case LogLevel.ERROR:
      method = 'error'
      break
  }

  // Log to console
  console[method](formattedMessage, levelStyle, messageStyle, ...args)
}

/**
 * Like log, but only logs a message once per session
 */
function logOnce(level: LogLevel, group: string, message: string, ...args: unknown[]): void {
  // Skip if already logged this message for this group and level
  if (hasLoggedBefore(group, level, message)) {
    return
  }

  // Mark message as logged
  markAsLogged(group, level, message)

  // Log the message
  log(level, group, message, ...args)
}

/**
 * Create a logger instance for a specific group
 * @param group The group name for this logger, or auto-determined from caller if not provided
 */
export function createLogger(group?: string) {
  // If no group name is provided, try to auto-determine it
  const loggerGroup = group || autoGroup()

  return {
    // Regular logging methods
    debug: (message: string, ...args: unknown[]) =>
      log(LogLevel.DEBUG, loggerGroup, message, ...args),

    info: (message: string, ...args: unknown[]) =>
      log(LogLevel.INFO, loggerGroup, message, ...args),

    warn: (message: string, ...args: unknown[]) =>
      log(LogLevel.WARN, loggerGroup, message, ...args),

    error: (message: string, ...args: unknown[]) =>
      log(LogLevel.ERROR, loggerGroup, message, ...args),

    // "Once" logging methods - only log each unique message once
    debugOnce: (message: string, ...args: unknown[]) =>
      logOnce(LogLevel.DEBUG, loggerGroup, message, ...args),

    infoOnce: (message: string, ...args: unknown[]) =>
      logOnce(LogLevel.INFO, loggerGroup, message, ...args),

    warnOnce: (message: string, ...args: unknown[]) =>
      logOnce(LogLevel.WARN, loggerGroup, message, ...args),

    errorOnce: (message: string, ...args: unknown[]) =>
      logOnce(LogLevel.ERROR, loggerGroup, message, ...args),

    // Allow direct access to check if this group's logs are enabled
    isEnabled: () => config.enabled && !config.disabledGroups.has(loggerGroup),
  }
}

/**
 * Utility configuration functions
 */
export const loggerConfig = {
  // Enable or disable all logging
  setEnabled(enabled: boolean): void {
    config.enabled = enabled
  },

  // Set the minimum log level
  setMinLevel(level: LogLevel): void {
    config.minLevel = level
  },

  // Disable logging for specific groups
  disableGroup(group: string): void {
    config.disabledGroups.add(group)
  },

  // Enable logging for a previously disabled group
  enableGroup(group: string): void {
    config.disabledGroups.delete(group)
  },

  // Toggle emoji symbols in logs
  setUseEmoji(useEmoji: boolean): void {
    config.useEmoji = useEmoji
  },

  // Get current configuration
  getConfig(): Readonly<DevLogConfig> {
    return {
      ...config,
      disabledGroups: new Set(config.disabledGroups),
    }
  },

  // Reset to default configuration
  reset(): void {
    config.enabled = typeof window !== 'undefined' && process.env.NODE_ENV === 'development'
    config.minLevel = LogLevel.DEBUG
    config.disabledGroups.clear()
    config.useEmoji = true
  },

  // Clear the "once" log memory - useful for testing or specific scenarios
  clearLoggedMessages(): void {
    loggedMessages.clear()
  },
}

// For backward compatibility
export const devLogConfig = loggerConfig

/**
 * Convenience method to quickly disable all logs in production
 * Place this in your app initialization if needed
 */
export function setupProductionLogging(): void {
  if (process.env.NODE_ENV === 'production') {
    config.minLevel = LogLevel.NONE
  }
}

/**
 * Default loggers for common application areas
 */
export const appLogger = createLogger('app')
export const apiLogger = createLogger('api')
export const storeLogger = createLogger('store')
export const routeLogger = createLogger('route')

// Example usage:
/*
import { createLogger } from '@/utils/logging';

// With explicit group name
const logger = createLogger('MovieComponent');

// With auto-detected group name (will use the calling file/function)
const logger = createLogger();

// In your component:
logger.debug('Rendering with props:', props);  // 🐛 [DEBUG] [MovieComponent] Rendering with props: {...}
logger.info('User action:', { id: 123, type: 'click' });  // ℹ️ [INFO] [MovieComponent] User action: {...}
logger.warn('Potential issue:', someValue);  // ⚠️ [WARN] [MovieComponent] Potential issue: {...}
logger.error('Failed to load data:', error);  // ❌ [ERROR] [MovieComponent] Failed to load data: {...}

// Prevent duplicate log messages in render loops:
function MyComponent() {
  // This will only log once, no matter how many times the component re-renders
  logger.warnOnce('This warning appears only once');

  return <div>...</div>;
}

// To disable this component's logs:
import { loggerConfig } from '@/utils/logging';
loggerConfig.disableGroup('MovieComponent');

// To disable emoji symbols:
loggerConfig.setUseEmoji(false);
*/
