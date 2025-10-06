import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import { GoogleAnalytics } from "@next/third-parties/google";
import { Providers } from "./providers";
import { ThemeScript } from "@/providers";
import ResponsiveShell from "@/components/ui/layout/ResponsiveShell";
import NavigationTracker from "@/components/analytics/NavigationTracker";
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
  icons: {
    icon: "/favicon.ico",
    apple: "/icons/apple-touch-icon.png",
    shortcut: "/favicon.ico",
  },
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  // Also supported by new API:
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "white" },
    { media: "(prefers-color-scheme: dark)", color: "***REMOVED***1a202c" },
  ],
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
        {/* Google Analytics - Modern Next.js approach */}
        <GoogleAnalytics gaId="G-KEFGRJ4SLR" />
        {/* Navigation Tracking */}
        <NavigationTracker />
      </body>
    </html>
  );
}
