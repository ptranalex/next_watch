import React from "react";

/**
 * A hook to safely unwrap Next.js 15 params
 *
 * @param params The params object from the page props
 * @returns The unwrapped params
 */
export function useParams<T>(params: Promise<T> | T): T {
  // In Next.js 15, params are a Promise that needs to be unwrapped
  return React.use(params as Promise<T>);
}

export default useParams;
