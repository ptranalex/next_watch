"use client";

import { ChakraProvider } from "@chakra-ui/react";
import { Inter } from "next/font/google";
import theme from "@/src/theme";
import NavBar from "@/components/layout/NavBar";
import { AuthProvider } from "@/src/context/AuthContext";
import { Providers } from "@/src/app/providers";
import { MovieQueryProvider } from "@/src/context/MovieQueryContext";
import { CacheProvider } from "@chakra-ui/next-js";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <CacheProvider>
          <ChakraProvider theme={theme}>
            <AuthProvider>
              <Providers>
                <MovieQueryProvider>
                  <NavBar />
                  <main>{children}</main>
                </MovieQueryProvider>
              </Providers>
            </AuthProvider>
          </ChakraProvider>
        </CacheProvider>
      </body>
    </html>
  );
}
