import type { MetadataRoute } from "next";
import { site } from "@/lib/site";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = site.url;
  const routes = ["", "/personal", "/business", "/kids", "/teens", "/about", "/pricing", "/method", "/curriculum", "/phuket", "/projects", "/parents", "/faq", "/start", "/privacy", "/terms", "/safety", "/en", "/en/personal", "/en/business", "/en/kids", "/en/teens", "/en/about", "/en/pricing", "/en/method", "/en/curriculum", "/en/phuket", "/en/projects", "/en/parents", "/en/faq", "/en/start", "/en/privacy", "/en/terms", "/en/safety"];
  return routes.map((route) => ({
    url: `${base}${route}`,
    changeFrequency: "monthly",
    priority: route === "" || route === "/en" ? 1 : 0.8,
  }));
}
