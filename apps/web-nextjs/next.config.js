/** @type {import('next').NextConfig} */
const nextConfig = {
  // Core settings
  reactStrictMode: true,
  skipTrailingSlashRedirect: true,

  // Required to fix pnpm module resolution issue
  transpilePackages: ["react-icons"],

  // Image optimization
  images: {
    domains: ["image.tmdb.org"], // Allow images from TMDB
  },

  // Build optimizations
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
    esmExternals: "loose", // Helps with pnpm compatibility
  },

  // Additional production optimizations
  productionBrowserSourceMaps: false, // Disable source maps in production

  // Webpack config for pnpm
  webpack: (config) => {
    // Add additional webpack configuration for pnpm compatibility
    config.module = {
      ...config.module,
      exprContextCritical: false, // Suppress warnings about dynamic requires
    };
    return config;
  },
};

module.exports = nextConfig;
