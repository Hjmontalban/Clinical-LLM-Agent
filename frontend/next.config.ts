import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  outputFileTracingRoot: path.join(__dirname),
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    if (apiUrl) {
      return [
        {
          source: "/api/:path*",
          destination: `${apiUrl.replace(/\/$/, "")}/api/:path*`,
        },
      ];
    }
    // Local dev: proxy /api to FastAPI (Vercel uses vercel.json instead)
    if (process.env.NODE_ENV === "development") {
      const port = process.env.BACKEND_PORT || "8002";
      return [
        {
          source: "/api/:path*",
          destination: `http://127.0.0.1:${port}/api/:path*`,
        },
      ];
    }
    return [];
  },
};

export default nextConfig;
