import config from "../config";

/**
 * Returns a complete poster image URL
 * @param path The poster path from API
 * @param size Optional size override
 * @returns The complete CDN URL
 */
export const getPosterUrl = (
  path: string | null | undefined,
  size?: string
): string | null => {
  if (!path) return null;

  // Check if it's already a complete URL
  if (path.startsWith("http")) {
    return path;
  }

  // Make sure path starts with a slash
  const formattedPath = path.startsWith("/") ? path : `/${path}`;
  return `${config.cdn.imagesCdnUrl}/${
    size || config.cdn.posterSize
  }${formattedPath}`;
};

/**
 * Returns a complete backdrop image URL
 * @param path The backdrop path from API
 * @param size Optional size override
 * @returns The complete CDN URL
 */
export const getBackdropUrl = (
  path: string | null | undefined,
  size?: string
): string | null => {
  if (!path) return null;

  // Check if it's already a complete URL
  if (path.startsWith("http")) {
    return path;
  }

  // Make sure path starts with a slash
  const formattedPath = path.startsWith("/") ? path : `/${path}`;
  return `${config.cdn.imagesCdnUrl}/${
    size || config.cdn.backdropSize
  }${formattedPath}`;
};

/**
 * Returns a complete profile image URL
 * @param path The profile path from API
 * @param size Optional size override
 * @returns The complete CDN URL
 */
export const getProfileUrl = (
  path: string | null | undefined,
  size?: string
): string | null => {
  if (!path) return null;

  // Check if it's already a complete URL
  if (path.startsWith("http")) {
    return path;
  }

  // Make sure path starts with a slash
  const formattedPath = path.startsWith("/") ? path : `/${path}`;
  return `${config.cdn.imagesCdnUrl}/${
    size || config.cdn.profileSize
  }${formattedPath}`;
};
