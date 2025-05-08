/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["react-icons"],
  experimental: {
    serverActions: {
      allowedOrigins: ["localhost:3000", "localhost", "127.0.0.1"],
    },
    esmExternals: "loose",
  },
  webpack: (config) => {
    // Add additional webpack configuration for pnpm compatibility
    config.module = {
      ...config.module,
      exprContextCritical: false, // Suppress warnings about dynamic requires
    };

    return config;
  },
};

export default nextConfig;
