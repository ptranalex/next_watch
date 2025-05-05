"use client";

import { ChakraProvider, ColorModeScript } from "@chakra-ui/react";
import { Inter } from "next/font/google";
import { usePathname, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import theme from "../theme";
import NavBar from "../components/layout/NavBar";
import AuthInitializer from "@/components/auth/AuthInitializer";
import { Providers } from "./providers";
import { MovieQueryProvider } from "../context/MovieQueryContext";
import LoadingIndicator from "../components/commons/LoadingIndicator";
import SessionExpiredModal from "@/components/commons/SessionExpiredModal";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [isChangingPage, setIsChangingPage] = useState(false);

  // Track page changes to show loading state
  useEffect(() => {
    setIsChangingPage(true);
    const timeout = setTimeout(() => setIsChangingPage(false), 300);
    return () => clearTimeout(timeout);
  }, [pathname, searchParams]);

  return (
    <html lang="en" data-theme="dark">
      <head>
        <ColorModeScript initialColorMode={theme.config.initialColorMode} />
      </head>
      <body className={inter.className}>
        <AuthInitializer />
        <ChakraProvider
          theme={theme}
          colorModeManager={{
            type: "localStorage",
            get: () => "dark",
            set: () => {},
          }}
        >
          <Providers>
            <MovieQueryProvider>
              <NavBar />
              {isChangingPage && <LoadingIndicator />}
              <SessionExpiredModal />
              <main>{children}</main>
            </MovieQueryProvider>
          </Providers>
        </ChakraProvider>
      </body>
    </html>
  );
}
