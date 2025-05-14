import { Inter } from "next/font/google";
import { Providers } from "./providers";
import type { Metadata, Viewport } from "next";
import AppShell from "@/components/layout/AppShell";
import ThemeScript from "@/components/providers/ThemeScript";

// Load Inter font
const inter = Inter({ subsets: ["latin"] });

// Add metadata using Next.js metadata API
export const metadata: Metadata = {
  title: {
    template: "%s | Next Watch",
    default: "Next Watch - Find Your Next Movie",
  },
  description: "Discover your next favorite movie with Next Watch",
};

// Sets browser toolbar color based on light/dark mode preference (mostly for mobile/pwa polish)
export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "white" },
    { media: "(prefers-color-scheme: dark)", color: "***REMOVED***171923" },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" data-theme="dark">
      <head>
        <ThemeScript />
      </head>
      <body className={`${inter.className} chakra-ui-dark`}>
        <Providers>
          <AppShell>{children}</AppShell>
        </Providers>
      </body>
    </html>
  );
}
