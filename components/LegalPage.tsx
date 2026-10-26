import type { ReactNode } from "react";
import { WorkshopEditorial } from "./workshop/WorkshopEditorial";

export function LegalPage({ title, intro, locale = "ru", path, children }: { title: string; intro: string; locale?: "ru" | "en"; path: "privacy" | "terms" | "safety"; children: ReactNode }) {
  return (
    <WorkshopEditorial locale={locale} alternateHref={locale === "ru" ? `/en/${path}` : `/${path}`} showReach={path === "safety"} light={path !== "safety"}>
      <main id="main" className="legalMain">
        <section className="legalHero"><div className="shell"><span className="kicker">{locale === "en" ? "AI SKILL LAB · POLICY" : "AI SKILL LAB · ПРАВИЛА"}</span><h1>{title}</h1><p>{intro}</p><div className="legalUpdated">{locale === "en" ? "Updated: 14 August 2026" : "Обновлено: 14 августа 2026"}</div></div></section>
        <section className="legalBody"><div className="shell legalProse">{children}</div></section>
      </main>
    </WorkshopEditorial>
  );
}
