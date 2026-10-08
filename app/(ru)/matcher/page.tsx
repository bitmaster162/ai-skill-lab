import type { Metadata } from "next";
import { WorkshopInteractive } from "@/components/workshop/WorkshopInteractive";
import { ProgramMatcher } from "@/components/ProgramMatcher";

export const metadata: Metadata = {
  title: { absolute: "Подобрать обучение ИИ — AI Skill Lab · Пхукет" },
  description: "AI-подбор маршрута по проверяемой таблице программ с локальным fallback. Ввод не хранится; brief отправляется только по согласию.",
  alternates: { canonical: "/matcher", languages: { ru: "/matcher", en: "/en/matcher" } },
  twitter: { card: "summary_large_image", title: "Подобрать AI-программу", description: "AI-подбор маршрута по проверяемой таблице программ с локальным fallback.", images: ["/og.png"] },
};

export default function Page(){return <WorkshopInteractive locale="ru" alternateHref="/en/matcher"><main id="main"><section className="hero heroR2"><div className="shell"><div className="eyebrow matcherEyebrow"><span className="dot"/> ПОДБОР ПРОГРАММЫ · ИИ + ЗАПАСНОЙ ВАРИАНТ</div><h1>Подобрать маршрут<br/><span>без выдуманных цен.</span></h1><p className="heroLead">Три выбора и цель дают стартовую рекомендацию только из опубликованной таблицы программ. ИИ используется по кнопке; при недоступности остаётся локальный запасной вариант.</p></div></section><section className="section"><div className="shell"><noscript><div className="matcherNoScript"><strong>JavaScript отключён.</strong><p>Подбор программы не сможет посчитать рекомендацию, но все пакеты и цены доступны без JavaScript.</p><div className="heroActions"><a className="button buttonPrimary" href="/pricing">Смотреть стоимость</a><a className="button buttonGhost" href="/start">Начать без подбор программы</a></div></div></noscript><ProgramMatcher/></div></section></main></WorkshopInteractive>}
