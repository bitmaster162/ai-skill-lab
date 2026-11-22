import type { MetadataRoute } from "next";
import { site } from "@/lib/site";
import { listGuides } from "@/lib/guides";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = site.url;
  const lastModified = "2026-10-16";
  const routes = ["", "/personal", "/business", "/certificate", "/kids", "/teens", "/about", "/pricing", "/method", "/curriculum", "/phuket", "/projects", "/parents", "/faq", "/family", "/matcher", "/challenge", "/proof", "/build", "/studio", "/start", "/privacy", "/terms", "/safety", "/guides", "/en", "/en/personal", "/en/business", "/en/certificate", "/en/kids", "/en/teens", "/en/about", "/en/pricing", "/en/method", "/en/curriculum", "/en/phuket", "/en/projects", "/en/parents", "/en/faq", "/en/family", "/en/matcher", "/en/challenge", "/en/proof", "/en/build", "/en/studio", "/en/start", "/en/privacy", "/en/terms", "/en/safety", "/en/guides"];
  const guideRoutes = [...listGuides("ru"), ...listGuides("en")].map((guide) => guide.meta.path);
  const universeRoutes = ["/phuket-universe", "/en/phuket-universe"];
  // Both language versions received new links or form navigation in the 21 November release.
  const november21Routes = new Set(
    ["", "/business", "/kids", "/matcher", "/method", "/parents", "/personal", "/pricing", "/teens"]
      .flatMap((route) => [route, `/en${route}`]),
  );
  const november22Routes = new Set([
    "/safety", "/start", "/guides",
    "/guides/ai-pilot-for-small-business", "/guides/ai-start-for-adults",
  ].flatMap((route) => [route, `/en${route}`]));
  november22Routes.add("/en/phuket-universe");
  const october26Routes = new Set(["/challenge", "/faq", "/phuket", "/privacy", "/projects", "/proof", "/studio", "/terms"]);

  function lastModifiedFor(route: string): string {
    if (november22Routes.has(route)) return "2026-11-22";
    if (november21Routes.has(route)) return "2026-11-21";
    if (october26Routes.has(route)) return "2026-10-26";
    if (universeRoutes.includes(route)) return "2026-10-15";
    return lastModified;
  }

  return [...routes, ...guideRoutes, ...universeRoutes].map((route) => ({
    url: new URL(route || "/", base).href,
    lastModified: lastModifiedFor(route),
    changeFrequency: "monthly",
    priority: route === "" || route === "/en" ? 1 : 0.8,
  }));
}
