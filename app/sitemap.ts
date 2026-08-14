import type { MetadataRoute } from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = process.env.NEXT_PUBLIC_SITE_URL || "https://example.com";
  const routes = ["", "/personal", "/business", "/kids", "/teens", "/about", "/start", "/privacy", "/terms", "/safety", "/en", "/en/personal", "/en/business", "/en/kids", "/en/teens", "/en/about", "/en/start", "/en/privacy", "/en/terms", "/en/safety"];
  return routes.map((route) => ({
    url: `${base}${route}`,
    changeFrequency: "monthly",
    priority: route === "" || route === "/en" ? 1 : 0.8,
  }));
}
