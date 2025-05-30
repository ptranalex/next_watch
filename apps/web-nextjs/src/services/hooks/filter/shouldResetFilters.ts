// useShouldResetFilters.ts
import { createLogger } from "@/utils/logging";

// Create logger for this utility
const logger = createLogger("shouldResetFilters");

export function shouldResetFilters(
  fromPath?: string,
  toPath?: string
): boolean {
  if (!fromPath || !toPath) {
    logger.debug("Missing path arguments, not resetting filters");
    return false;
  }

  const stripParams = (path: string) => path.split("?")[0];

  const from = stripParams(fromPath);
  const to = stripParams(toPath);

  // Example of contexts that should reset
  const isFromHome = from === "/";
  const isToBrowse = to.startsWith("/browse");
  const isCrossContext =
    (from.startsWith("/top/") && !to.startsWith("/top/")) ||
    (from.startsWith("/genres/") && !to.startsWith("/genres/"));

  // Log the decision factors
  logger.debug(`Evaluating route change for filter reset:`, {
    from,
    to,
    isFromHome,
    isCrossContext,
    isToBrowse,
  });

  // Logic: reset if changing main context or from home
  const shouldReset = isFromHome || isCrossContext || isToBrowse;

  if (shouldReset) {
    logger.info(`Will reset filters for route change: ${from} → ${to}`);
  }

  return shouldReset;
}
