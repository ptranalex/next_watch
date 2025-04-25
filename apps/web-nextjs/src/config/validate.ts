import { validateConfig } from "./index";

/**
 * Validates the application configuration at runtime.
 * This function checks if all required environment variables are set.
 * It will log warnings in development and can throw errors in production.
 *
 * @param throwOnError Whether to throw an error if validation fails
 * @returns True if validation passes, false otherwise
 */
export const validateRuntimeConfig = (throwOnError = false): boolean => {
  const issues = validateConfig();

  if (issues.length === 0) {
    return true;
  }

  // In development, we'll just log warnings
  if (process.env.NODE_ENV === "development") {
    console.warn("⚠️ Configuration validation warnings:");
    issues.forEach((issue) => console.warn(`  - ${issue}`));
    console.warn("Please check your .env.local file and update accordingly.");
  }
  // In production, we might want to be more strict
  else if (throwOnError) {
    throw new Error(`Configuration validation failed: ${issues.join(", ")}`);
  }

  return false;
};

export default validateRuntimeConfig;
