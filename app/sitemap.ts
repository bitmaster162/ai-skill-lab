import type { MetadataRoute } from "next";
import { site } from "@/lib/site";
import { listGuides } from "@/lib/guides";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = site.url;
  const lastModified = "2026-10-11";
  const routeLastModified: Record<string, string> = {
  "/en": "2026-10-14",
  "/en/guides/ai-safety-for-kids": "2026-10-14",
  "/en/start": "2026-10-14",
  "/start": "2026-10-14"
};
  const routes = ["", "/personal", "/business", "/certificate", "/kids", "/teens", "/about", "/pricing", "/method", "/curriculum", "/phuket", "/projects", "/parents", "/faq", "/family", "/matcher", "/challenge", "/proof", "/build", "/studio", "/start", "/privacy", "/terms", "/safety", "/guides", "/en", "/en/personal", "/en/business", "/en/certificate", "/en/kids", "/en/teens", "/en/about", "/en/pricing", "/en/method", "/en/curriculum", "/en/phuket", "/en/projects", "/en/parents", "/en/faq", "/en/family", "/en/matcher", "/en/challenge", "/en/proof", "/en/build", "/en/studio", "/en/start", "/en/privacy", "/en/terms", "/en/safety", "/en/guides"];
  const guideRoutes = [...listGuides("ru"), ...listGuides("en")].map((guide) => guide.meta.path);
  return [...routes, ...guideRoutes].map((route) => ({
    url: `${base}${route}`,
    lastModified: routeLastModified[route] || lastModified,
    changeFrequency: "monthly",
    priority: route === "" || route === "/en" ? 1 : 0.8,
  }));
}
