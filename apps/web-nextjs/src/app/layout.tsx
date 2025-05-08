"use client";

import { ColorModeScript } from "@chakra-ui/react";
import { Inter } from "next/font/google";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import theme from "../theme";
import NavBar from "../components/layout/NavBar";
import { Providers } from "./providers";
import LoadingIndicator from "../components/commons/LoadingIndicator";

// No longer need to mark as dynamic since we're not using useSearchParams
// export const dynamic = "force-dynamic";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const [isChangingPage, setIsChangingPage] = useState(false);

  // Track page changes to show loading state
  useEffect(() => {
    setIsChangingPage(true);
    const timeout = setTimeout(() => setIsChangingPage(false), 300);
    return () => clearTimeout(timeout);
  }, [pathname]); // Removed searchParams dependency

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
