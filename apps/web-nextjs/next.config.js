/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  skipTrailingSlashRedirect: true,
  images: {
    domains: ["image.tmdb.org"], // Allow images from TMDB
  },
  eslint: {
    // Handled through separate process
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Handled through separate process
    ignoreBuildErrors: true,
  },
  output: "standalone", // This setting is critical for Docker deployments

  // Experimental features - only keep what's necessary
  experimental: {
    // Allow server actions from specific origins
    serverActions: {
      allowedOrigins: ["*"],
    },
  },

  // Additional production optimizations
  productionBrowserSourceMaps: false, // Disable source maps in production
};

module.exports = nextConfig;
