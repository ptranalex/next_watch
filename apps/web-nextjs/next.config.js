/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ["image.tmdb.org"], // Allow images from TMDB
  },
  // Enable API routes
  api: {
    bodyParser: {
      sizeLimit: "1mb",
    },
  },
};

module.exports = nextConfig;
