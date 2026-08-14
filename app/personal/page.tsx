import type { Metadata } from "next";
import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

export const metadata: Metadata = {
  title: "Персональное обучение AI",
  description: "Персональное обучение AI 1-на-1 для работы, исследований, автоматизаций и личных AI-процессов — Phuket и online.",
  alternates: { canonical: "/personal", languages: { ru: "/personal", en: "/en/personal" } },
};

const stages = [
  ["01", "Диагностика", "Уровень, повторяемые задачи, ограничения и целевой результат."],
  ["02", "Спецификация", "Контекст, критерии качества и проверки вместо расплывчатых запросов."],
  ["03", "Сборка", "Reusable workflows, шаблоны, automation или agent."],
  ["04", "Проверка", "Источники, edge cases, failure modes и границы модели."],
  ["05", "Релиз", "Законченный проект, который можно использовать, показать и объяснить."],
];

export default function PersonalPage() {
  return <><Header alternateHref="/en/personal"/><main>
    <section className="teenHero"><div className="shell teenHeroGrid"><div><span className="eyebrow">Взрослым · 1-на-1</span><h1>Превратить AI из окна чата<br/><span>в рабочую систему.</span></h1><p>Исследования, тексты, анализ, автоматизации и ассистенты вокруг ваших реальных задач — без одинаковой программы для всех.</p><div className="heroActions"><Link className="button buttonLight" href="/start">Обсудить маршрут</Link></div></div></div></section>
    <section className="section"><div className="shell"><span className="kicker">Метод</span><h2>Цель → система → результат</h2><div className="steps">{stages.map(([n,t,x])=><article key={n}><span>{n}</span><h3>{t}</h3><p>{x}</p></article>)}</div></div></section>
    <section className="section sectionInk" id="builder"><div className="shell splitHead"><div><span className="kicker kickerLight">AI Builder</span><h2>Не только prompting.<br/><em>Сборка систем.</em></h2></div><p>Ассистенты, автоматизации, agents, простые product prototypes и практические технические workflows.</p></div></section>
    <section className="section" id="pricing"><div className="shell"><span className="kicker">Стоимость</span><h2>Выбрать глубину</h2><div className="pricingGrid"><article className="priceCard"><span className="cardMeta">Start</span><h3>4 занятия</h3><div className="price">$390</div><p>Базовый рабочий процесс и первый полезный результат.</p></article><article className="priceCard featuredPrice"><span className="cardMeta">Personal</span><h3>10 занятий</h3><div className="price">$890</div><p>Полная персональная траектория и законченный проект.</p></article><article className="priceCard"><span className="cardMeta">Intensive</span><h3>12 + проект</h3><div className="price">$1,290</div><p>Automation, AI-agent, mini-product или технический portfolio project.</p></article></div></div></section>
  </main><Footer/></>;
}
