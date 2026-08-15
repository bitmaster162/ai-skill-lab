import type { Metadata } from "next";
import Link from "next/link";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "Примерные AI-проекты",
  description: "Примеры учебных AI-проектов для детей, подростков, взрослых и бизнеса — без выдачи примеров за реальные клиентские кейсы.",
  alternates: { canonical: "/projects", languages: { ru: "/projects", en: "/en/projects" } },
};

const groups = [
  ["8–13", "Создать и объяснить.", [
    ["01 · RESEARCH", "Детектив фактов", "Тема → 3+ источника → таблица утверждений → короткая презентация «что подтвердилось / что нет»."],
    ["02 · CREATE", "Мир и персонаж", "Character bible, визуальные правила, storyboard и итоговая мини-история с явным разделением своей идеи и AI-помощи."],
    ["03 · LOGIC", "Мини-игра", "Правила, состояния, простая логика и прототип, который ребёнок может объяснить."],
  ]],
  ["14–18", "Собрать в portfolio.", [
    ["04 · STUDY", "Research OS", "Шаблон исследования: вопрос, источники, тезисы, проверка, итоговый memo и presentation."],
    ["05 · BUILD", "AI assistant prototype", "Простой ассистент или workflow под реальную задачу: input, rules, output, failure cases и README."],
    ["06 · PRODUCT", "Mini-product", "Проблема пользователя, прототип, тестовые сценарии, ограничения и короткий demo."],
  ]],
  ["Adults / business", "Артефакт, который остаётся после занятий.", [
    ["07 · WORKFLOW", "Personal research workflow", "Повторяемая система поиска, сравнения источников, synthesis и проверки."],
    ["08 · AUTOMATION", "Process prototype", "Ассистент или automation для одного повторяемого процесса с ownership и fallback."],
    ["09 · PLAYBOOK", "AI operating rules", "Шаблоны задач, критерии проверки, data boundaries и инструкции для повторного использования."],
  ]],
] as const;

export default function Page() {
  return <><Header contactHref="/start" alternateHref="/en/projects"/><main id="main">
    <section className="hero heroR2"><div className="shell"><div className="eyebrow"><span className="dot"/> EXAMPLE OUTPUTS · NOT TESTIMONIALS</div><h1>Показать результат,<br/><span>а не обещание.</span></h1><p className="heroLead">Ниже — примеры форматов проектов, которые можно собрать в рамках обучения. Это не заявления о конкретных клиентах или учениках.</p></div></section>
    {groups.map(([label,title,items])=><section className="section" key={label}><div className="shell"><div className="sectionHead"><span className="kicker">{label}</span><h2>{title}</h2></div><div className="programGrid">{items.map(([m,t,d])=><article className="programCard" key={m}><span className="cardMeta">{m}</span><div className="cardSpacer"/><h3>{t}</h3><p>{d}</p></article>)}</div></div></section>)}
    <section className="section sectionMuted"><div className="shell"><div className="sectionHead"><span className="kicker">Start</span><h2>Выберем проект под реальный интерес.</h2><p>Примеры выше — не обязательная программа. Итоговый проект подбирается под цель, возраст и глубину.</p></div><Link className="button buttonPrimary" href="/start">Подобрать маршрут →</Link></div></section>
  </main><Footer/></>;
}
