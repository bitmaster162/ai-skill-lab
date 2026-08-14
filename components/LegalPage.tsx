import type { ReactNode } from "react";
import { Footer } from "./Footer";
import { Header } from "./Header";

export function LegalPage({ title, intro, locale = "ru", path, children }: { title: string; intro: string; locale?: "ru" | "en"; path: "privacy" | "terms" | "safety"; children: ReactNode }) {
  return (
    <>
      <Header locale={locale} alternateHref={locale === "ru" ? `/en/${path}` : `/${path}`} />
      <main className="legalMain">
        <section className="legalHero"><div className="shell"><span className="kicker">AI SKILL LAB · POLICY</span><h1>{title}</h1><p>{intro}</p><div className="legalUpdated">{locale === "en" ? "Updated: 14 August 2026" : "Обновлено: 14 августа 2026"}</div></div></section>
        <section className="legalBody"><div className="shell legalProse">{children}</div></section>
      </main>
      <Footer locale={locale} />
    </>
  );
}
