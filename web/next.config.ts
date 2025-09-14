import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  compiler: {
    reactRemoveProperties: false,
  },
};

export default nextConfig;
