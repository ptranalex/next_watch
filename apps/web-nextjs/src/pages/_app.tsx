import React, { useEffect } from "react";
import { ChakraProvider, ColorModeScript } from "@chakra-ui/react";
import { GoogleOAuthProvider } from "@react-oauth/google";
import {
  Hydrate,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import type { AppProps } from "next/app";
import Layout from "../components/layout/Layout";
import theme from "../theme";
import config from "../config";
import validateRuntimeConfig from "../config/validate";

// Create a client
function MyApp({ Component, pageProps }: AppProps) {
  // Create a new QueryClient for each request in development
  // This ensures data is not shared between connections
  const [queryClient] = React.useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            cacheTime: 5 * 60 * 1000, // 5 minutes
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  // Validate configuration during development
  useEffect(() => {
    if (config.isDevelopment) {
      validateRuntimeConfig();
    }
  }, []);

  return (
    <GoogleOAuthProvider
      clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || ""}
    >
      <ChakraProvider
        theme={theme}
        toastOptions={{ defaultOptions: { position: "top" } }}
      >
        <ColorModeScript initialColorMode={theme.config.initialColorMode} />
        <QueryClientProvider client={queryClient}>
          <Hydrate state={pageProps.dehydratedState}>
            <Layout>
              <Component {...pageProps} />
            </Layout>
          </Hydrate>
          {config.isDevelopment && <ReactQueryDevtools />}
        </QueryClientProvider>
      </ChakraProvider>
    </GoogleOAuthProvider>
  );
}

export default MyApp;
