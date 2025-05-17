import useMovieFilterStore from "@/store/movieFilterStore";
import { createLogger } from "@/utils/logging";

// Create logger for this hook
const logger = createLogger("useBuildMovieUrl");

export function useBuildMovieUrl() {
  const { filters } = useMovieFilterStore();

  // Log hook initialization
  logger.debug("useBuildMovieUrl initialized");

  function buildUrl(basePath: string): string {
    logger.debug(`Building URL with base path: ${basePath}`);

    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        params.set(key, String(value));
        logger.debug(`Added param: ${key}=${value}`);
      }
    });

    const query = params.toString();
    const finalUrl = `${basePath}${query ? `?${query}` : ""}`;

    logger.debug(`Built URL: ${finalUrl}`);
    return finalUrl;
  }

  return buildUrl;
}

export default useBuildMovieUrl;
