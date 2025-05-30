"use client";

import { AuthProvider, ResponsiveProvider } from "@/providers";
import theme from "@/theme";
import { createLogger } from "@/utils/logging";
import { ChakraProvider } from "@chakra-ui/react";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import {
  CacheConfig,
  createCacheManager,
  GlobalCacheUtils,
} from "@/services/cache";
import React, { useEffect, useState } from "react";

// Create logger for this component
const logger = createLogger("Providers");

/**
 * Global providers component
 * Responsible only for setting up context providers, not UI elements
 * The order matters - providers higher in the tree can be accessed by providers lower down
 */
export function Providers({ children }: { children: React.ReactNode }) {
  // Log provider initialization
  useEffect(() => {
    logger.info("Application providers initializing");

    return () => {
      logger.debug("Application providers unmounting");
    };
  }, []);

  const [queryClient] = useState(() => {
    logger.debug("Creating QueryClient with optimized cache configuration");

    const client = new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: CacheConfig.defaultStaleTime, // 2 minutes
          cacheTime: CacheConfig.defaultGcTime, // 10 minutes (will be gcTime in v5)
          refetchOnWindowFocus: false,
          refetchOnMount: false,
          retry: 1,
        },
        mutations: {
          retry: 1,
        },
      },
    });

    // Initialize cache manager for advanced cache operations
    const cacheManager = createCacheManager(client);
    logger.debug("Cache manager initialized", {
      staleTime: CacheConfig.defaultStaleTime,
      cacheTime: CacheConfig.defaultGcTime,
    });

    // Store cache manager on client for global access
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (client as any).cacheManager = cacheManager;

    // Initialize global cache utilities for non-React usage
    GlobalCacheUtils.initialize(cacheManager);
    logger.debug("Global cache utilities initialized");

    return client;
  });

  // Check for required environment variables
  useEffect(() => {
    if (!process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID) {
      logger.warn(
        "NEXT_PUBLIC_GOOGLE_CLIENT_ID is not defined - Google authentication may not work"
      );
    }
  }, []);

  return (
    <>
      {/* 1. Setup UI framework */}
      <ChakraProvider theme={theme} resetCSS={true}>
        {/* 2. Setup responsive detection */}
        <ResponsiveProvider>
          {/* 3. Setup data fetching with enhanced cache system */}
          <QueryClientProvider client={queryClient}>
            {/* 4. Setup authentication */}
            <GoogleOAuthProvider
              clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ""}
            >
              <AuthProvider>
                {/* 5. Setup app-specific state */}
                {children}
                <ReactQueryDevtools initialIsOpen={false} />
              </AuthProvider>
            </GoogleOAuthProvider>
          </QueryClientProvider>
        </ResponsiveProvider>
      </ChakraProvider>
    </>
  );
}
