import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./i18n/request.ts");

/**
 * Production builds MUST have a real backend URL: `NEXT_PUBLIC_API_BASE_URL`
 * is inlined into the client bundle at build time. Without it the bundle
 * defaults to http://localhost:8000, which fails for every deployed visitor
 * (Vercel page → browser-blocked loopback). Shout it in the build log so the
 * mistake is caught in the Dashboard instead of in the browser console.
 */
const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
const isProdBuild = process.env.NODE_ENV === "production";
const looksLocal = !apiBase || /^(https?:)?\/\/(localhost|127\.0\.0\.1)/.test(apiBase);
if (isProdBuild && looksLocal) {
  console.error(
    "\n" +
      "!".repeat(76) +
      "\n!!  GrowLocal: NEXT_PUBLIC_API_BASE_URL is MISSING or points at localhost.\n" +
      "!!  This build will call the visitor's own machine and every API request\n" +
      "!!  will fail (CORS / ERR_FAILED). SetNEXT_PUBLIC_API_BASE_URL to the\n" +
      "!!  deployed backend origin (e.g. https://growlocal-api.vercel.app) in this\n" +
      "!!  project's Environment Variables and REDEPLOY.\n" +
      "!".repeat(76) +
      "\n"
  );
}

const nextConfig: NextConfig = {
  reactStrictMode: true,
};

export default withNextIntl(nextConfig);
