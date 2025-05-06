"use client";

import { ColorModeScript } from "@chakra-ui/react";
import { Inter } from "next/font/google";
import { usePathname, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import theme from "../theme";
import NavBar from "../components/layout/NavBar";
import { Providers } from "./providers";
import LoadingIndicator from "../components/commons/LoadingIndicator";

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
        <Providers>
          <NavBar />
          {isChangingPage && <LoadingIndicator />}
          <main>{children}</main>
        </Providers>
      </body>
    </html>
  );
}
