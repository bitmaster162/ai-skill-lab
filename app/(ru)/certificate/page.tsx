import type { Metadata } from "next";
import Link from "next/link";
import { WorkshopEditorial } from "@/components/workshop/WorkshopEditorial";

export const metadata: Metadata = {
  title: { absolute: "Сертификат об обучении ИИ — AI Skill Lab · Пхукет" },
  description: "Как AI Skill Lab оформляет completion record: проверяемый проект, запись о завершении, отдельное согласие на публикацию и zero-PII для детей.",
  alternates: { canonical: "/certificate", languages: { ru: "/certificate", en: "/en/certificate" } },
};

const record = [
  ["01","Завершённый scope","Запись может фиксировать только реально завершённую согласованную программу или проект — не посещение ради посещения."],
  ["02","Проверяемый артефакт","Основа результата — проект, workflow, исследование, прототип или другая работа, которую ученик способен объяснить и проверить."],
  ["03","Личный вклад","AI может помогать, но completion record не заменяет проверку того, что ученик понимает собственные решения и вклад."],
  ["04","Границы","Это не аккредитация, не школьный или университетский кредит, не профессиональная квалификация и не security/compliance certification."],
];

export default function Page(){
  return <WorkshopEditorial locale="ru" alternateHref="/en/certificate" contactHref="/start"><main id="main">
    <section className="hero heroR2"><div className="shell"><div className="eyebrow"><span className="dot"/> N25 · COMPLETION RECORD · CONSENT-BOUND</div><h1>Сначала проект.<br/><span>Потом запись.</span></h1><p className="heroLead">AI Skill Lab может оформить запись о завершении обучения ИИ после реальной работы. Сертификат не является главным результатом программы и не превращает обучение в аккредитацию или внешнюю квалификацию.</p></div></section>
    <section className="section"><div className="shell"><div className="sectionHead"><span className="kicker">WHAT IT CAN PROVE</span><h2>Фиксируем завершение.<br/>Не присваиваем квалификацию.</h2><p>Completion record привязан к факту завершённой работы и её проверяемому результату. Он не должен обещать больше, чем реально подтверждено.</p></div><div className="steps">{record.map(([n,t,d])=><article key={n}><span>{n}</span><h2>{t}</h2><p>{d}</p></article>)}</div></div></section>
    <section className="section sectionMuted"><div className="shell"><div className="sectionHead"><span className="kicker">TEMPLATE · NOT ISSUED</span><h2>На этой странице нет<br/>реального ученика.</h2><p>Текущий публичный route показывает только политику и шаблон. Никакой student record не выпущен и никакая личность не заявлена.</p></div><div className="steps"><article><span>01</span><h2>Статус</h2><p>TEMPLATE · NOT ISSUED</p></article><article><span>02</span><h2>Ученик</h2><p>Не опубликован. Реального имени или идентификатора здесь нет.</p></article><article><span>03</span><h2>Основание</h2><p>Проектная работа + способность объяснить результат.</p></article><article><span>04</span><h2>Публичная проверка</h2><p>Не включена. Реальный verification record требует отдельного owner-approved факта и consent.</p></article></div></div></section>
    <section className="section"><div className="shell"><div className="sectionHead"><span className="kicker">CONSENT & YOUTH PRIVACY</span><h2>По умолчанию — приватно.</h2><p>Публичная запись появляется только после отдельного согласия на публикацию. Если такого согласия нет, запись не публикуется.</p></div><div className="steps"><article><span>A</span><h2>Совершеннолетние</h2><p>Имя или другие идентификаторы могут появиться только после отдельного явного согласия и проверки фактов владельцем.</p></article><article><span>B</span><h2>Несовершеннолетние</h2><p>Публичная страница не должна содержать имя, возраст, фото, школу, контакт, username, account/repository links или другие персональные идентификаторы. Организационный контакт ведёт взрослый.</p></article><article><span>C</span><h2>Нет согласия</h2><p>Нет публичной student record. Частный результат и проект остаются отдельными от публичного сайта.</p></article><article><span>D</span><h2>Запросы по данным</h2><p>Правила заявок и запросов на исправление или удаление описаны в политике конфиденциальности.</p></article></div><div className="heroActions"><Link className="button buttonPrimary" href="/projects">Смотреть реальные проекты →</Link><Link className="button buttonGhost" href="/privacy">Конфиденциальность →</Link></div></div></section>
  </main></WorkshopEditorial>;
}
