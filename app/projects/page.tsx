import type { Metadata } from "next";
import Link from "next/link";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { ProjectStudio } from "@/components/ProjectStudio";

export const metadata: Metadata = {
  title: "Project Studio — примерные AI-проекты",
  description: "Интерактивная витрина примерных AI-проектов: задача, роль AI, human verification и итоговый артефакт. Это примеры, не клиентские кейсы.",
  alternates: { canonical: "/projects", languages: { ru: "/projects", en: "/en/projects" } },
};

export default function Page() {
  return <><Header contactHref="/start" alternateHref="/en/projects"/><main id="main">
    <section className="projectStudioHero"><div className="shell"><div className="eyebrow"><span className="dot"/> EXAMPLE OUTPUTS · NOT TESTIMONIALS</div><h1>Не галерея работ.<br/><span>Project Studio.</span></h1><p className="heroLead">9 примерных форматов показывают не только что можно собрать, но и как устроена хорошая AI-работа: цель → роль AI → human check → проверяемый артефакт. Это не заявления о конкретных клиентах или учениках.</p><div className="actions"><a className="button buttonPrimary" href="#studio">Исследовать проекты ↓</a><Link className="button buttonGhost" href="/proof">Как мы проверяем AI →</Link></div></div></section>
    <section className="projectStudioSection" id="studio"><div className="shell"><div className="sectionHead projectStudioIntro"><span className="kicker">PROJECT STUDIO / 9 EXAMPLES</span><h2>Фильтруй по типу работы.<br/>Смотри на устройство результата.</h2><p>Весь контент доступен даже без JavaScript. Фильтр работает только локально в браузере и ничего не отправляет наружу.</p></div><ProjectStudio/></div></section>
    <section className="section sectionMuted"><div className="shell projectStudioCta"><div className="sectionHead"><span className="kicker">Build yours</span><h2>Пример — не программа.<br/>Проект строится вокруг реальной цели.</h2><p>Выбираем уровень, задачу и глубину, затем фиксируем критерии результата до старта.</p></div><div className="actions"><Link className="button buttonPrimary" href="/matcher">Подобрать маршрут →</Link><Link className="button buttonGhost" href="/start">Описать задачу →</Link></div></div></section>
  </main><Footer/></>;
}
