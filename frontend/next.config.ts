import type { NextConfig } from "next";
import os from "os";

function getLanIPs(): string[] {
  const ips: string[] = [];
  for (const iface of Object.values(os.networkInterfaces())) {
    for (const alias of iface ?? []) {
      if (alias.family === "IPv4" && !alias.internal) ips.push(alias.address);
    }
  }
  return ips;
}

const nextConfig: NextConfig = {
  // Allow LAN devices (phone, tablet) to access the dev server
  allowedDevOrigins: getLanIPs(),
};

export default nextConfig;
