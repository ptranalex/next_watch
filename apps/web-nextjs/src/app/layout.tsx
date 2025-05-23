import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { Providers } from "./providers";
import { ThemeScript } from "@/providers";
import ResponsiveShell from "@/components/ui/templates/ResponsiveShell";
import "./globals.css";

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
  // Add mobile viewport settings
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <ThemeScript />
      </head>
      <body className={inter.className}>
        <Providers>
          <ResponsiveShell>{children}</ResponsiveShell>
        </Providers>
      </body>
    </html>
  );
}
