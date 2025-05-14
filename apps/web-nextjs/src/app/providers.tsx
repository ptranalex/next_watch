"use client";

import React, { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { GoogleOAuthProvider } from "@react-oauth/google";
import AuthProvider from "@/components/providers/AuthProvider";
import { ChakraProvider } from "@chakra-ui/react";
import theme from "../theme";
import { MovieQueryProvider } from "../context/MovieQueryContext";

/**
 * Global providers component
 * Responsible only for setting up context providers, not UI elements
 * The order matters - providers higher in the tree can be accessed by providers lower down
 */
export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 10 * 60 * 1000, // 10 minutes
            cacheTime: 60 * 60 * 1000, // 60 minutes
            refetchOnWindowFocus: false,
            refetchOnMount: false,
            retry: 1,
          },
        },
      })
  );

  return (
    <>
      {/* 1. Setup UI framework */}
      <ChakraProvider theme={theme} resetCSS={true}>
        {/* 2. Setup data fetching */}
        <QueryClientProvider client={queryClient}>
          {/* 3. Setup authentication */}
          <GoogleOAuthProvider
            clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ""}
          >
            <AuthProvider>
              {/* 4. Setup app-specific state */}
              <MovieQueryProvider>
                {children}
                <ReactQueryDevtools initialIsOpen={false} />
              </MovieQueryProvider>
            </AuthProvider>
          </GoogleOAuthProvider>
        </QueryClientProvider>
      </ChakraProvider>
    </>
  );
}
