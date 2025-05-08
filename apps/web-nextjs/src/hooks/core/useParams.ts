"use client";

import { useEffect, useState } from "react";

/**
 * A hook to safely unwrap Next.js params in client components
 *
 * @param params The params object from the page props
 * @returns The unwrapped params
 */
export function useParams<T>(params: Promise<T> | T): T {
  const [resolvedParams, setResolvedParams] = useState<T | null>(null);

  useEffect(() => {
    // If params is a Promise, resolve it
    if (params instanceof Promise) {
      params.then((result) => {
        setResolvedParams(result);
      });
    } else {
      // If params is already resolved, just use it
      setResolvedParams(params);
    }
  }, [params]);

  // Return the resolved params or an empty object as fallback
  return resolvedParams || ({} as T);
}

export default useParams;
