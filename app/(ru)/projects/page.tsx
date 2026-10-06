import type { Metadata } from "next";
import { WorkshopInteractive } from "@/components/workshop/WorkshopInteractive";
import Link from "next/link";
import { ProjectStudio } from "@/components/ProjectStudio";
import { RealProjectGallery } from "@/components/RealProjectGallery";

export const metadata: Metadata = {
  title: { absolute: "Projects — реальные AI-проекты — AI Skill Lab · Phuket" },
  description: "Публично проверяемые AI-проекты Роберта Думаняна и 9 примерных учебных форматов: evidence, границы claims, роль AI и human verification.",
  alternates: { canonical: "/projects", languages: { ru: "/projects", en: "/en/projects" } },
};

export default function Page() {
  return <WorkshopInteractive locale="ru" alternateHref="/en/projects"><main id="main">
    <section className="projectStudioHero"><div className="shell"><div className="eyebrow"><span className="dot"/> REAL BUILDS · PUBLIC PROVENANCE</div><h1>Реальные сборки.<br/><span>И Project Studio.</span></h1><p className="heroLead">Сначала — публичные проекты Роберта с проверяемыми репозиториями и честными границами claims. Ниже — 9 учебных примерных форматов; это не клиентские кейсы и не работы учеников.</p><div className="actions"><a className="button buttonPrimary" href="#real-projects">Смотреть реальные проекты ↓</a><Link className="button buttonGhost" href="/proof">Как мы проверяем AI →</Link></div></div></section>
    <section className="projectStudioSection" id="real-projects"><div className="shell"><div className="sectionHead projectStudioIntro"><span className="kicker">REAL BUILDS / 5 PUBLIC REPOS</span><h2>Публичный код.<br/>Явные границы claims.</h2><p>Пять проектов Роберта Думаняна с открытыми репозиториями и проверяемым scope. Это проекты наставника, не работы учеников и не клиентские кейсы.</p></div><RealProjectGallery locale="ru"/></div></section>
    <section className="projectStudioSection" id="studio"><div className="shell"><div className="sectionHead projectStudioIntro"><span className="kicker">EXAMPLE OUTPUTS · NOT TESTIMONIALS / 9 EXAMPLES</span><h2>Фильтруй по типу работы.<br/>Смотри на устройство результата.</h2><p>Ниже — учебные примерные форматы, а не заявления о конкретных клиентах или учениках. Весь контент доступен даже без JavaScript; фильтр работает только локально в браузере и ничего не отправляет наружу.</p></div><ProjectStudio/></div></section>
    <section className="section sectionMuted"><div className="shell projectStudioCta"><div className="sectionHead"><span className="kicker">Build yours</span><h2>Пример — не программа.<br/>Проект строится вокруг реальной цели.</h2><p>Выбираем уровень, задачу и глубину, затем фиксируем критерии результата до старта.</p></div><div className="actions"><Link className="button buttonPrimary" href="/matcher">Подобрать маршрут →</Link><Link className="button buttonGhost" href="/start">Описать задачу →</Link></div></div></section>
  </main></WorkshopInteractive>;
}
