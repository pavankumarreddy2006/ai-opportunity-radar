import type { NextConfig } from "next";

const rawApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const apiBaseUrl = rawApiBaseUrl.startsWith("http") ? rawApiBaseUrl : `https://${rawApiBaseUrl}`;

const nextConfig: NextConfig = {
  typedRoutes: true,
  async rewrites() {
    return [
      {
        source: "/health",
        destination: `${apiBaseUrl}/health`,
      },
      {
        source: "/news",
        destination: `${apiBaseUrl}/news`,
      },
      {
        source: "/top5",
        destination: `${apiBaseUrl}/top5`,
      },
      {
        source: "/trending",
        destination: `${apiBaseUrl}/trending`,
      },
      {
        source: "/dashboard",
        destination: `${apiBaseUrl}/dashboard`,
      },
      {
        source: "/weekly-report",
        destination: `${apiBaseUrl}/weekly-report`,
      },
      {
        source: "/docs",
        destination: `${apiBaseUrl}/docs`,
      },
      {
        source: "/openapi.json",
        destination: `${apiBaseUrl}/openapi.json`,
      },
      {
        source: "/update-news",
        destination: `${apiBaseUrl}/update-news`,
      },
    ];
  },
};

export default nextConfig;
