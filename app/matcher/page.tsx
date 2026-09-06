import type { Metadata } from "next";
import { WorkshopInteractive } from "@/components/workshop/WorkshopInteractive";
import { ProgramMatcher } from "@/components/ProgramMatcher";

export const metadata: Metadata = {
  title: "Подобрать AI-программу",
  description: "Локальный program matcher: взрослый, ребёнок, подросток или business pilot. Ничего не отправляется и не сохраняется.",
  alternates: { canonical: "/matcher", languages: { ru: "/matcher", en: "/en/matcher" } },
  twitter: { card: "summary_large_image", title: "Подобрать AI-программу", description: "Локальный program matcher: взрослый, ребёнок, подросток или business pilot. Ничего не отправляется и не сохраняется.", images: ["/opengraph-image"] },
};

export default function Page(){return <WorkshopInteractive locale="ru" alternateHref="/en/matcher"><main id="main"><section className="hero heroR2"><div className="shell"><div className="eyebrow matcherEyebrow"><span className="dot"/> PROGRAM MATCHER · LOCAL ONLY</div><h1>Подобрать маршрут<br/><span>без анкеты.</span></h1><p className="heroLead">Три выбора дают стартовую рекомендацию по формату и пакету. Никакие ответы не отправляются на сервер и не сохраняются.</p></div></section><section className="section"><div className="shell"><noscript><div className="matcherNoScript"><strong>JavaScript отключён.</strong><p>Matcher не сможет посчитать рекомендацию, но все пакеты и цены доступны без JavaScript.</p><div className="heroActions"><a className="button buttonPrimary" href="/pricing">Смотреть стоимость</a><a className="button buttonGhost" href="/start">Начать без matcher</a></div></div></noscript><ProgramMatcher/></div></section></main></WorkshopInteractive>}
