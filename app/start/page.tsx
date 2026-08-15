import type { Metadata } from "next";
import Link from "next/link";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { CopyBriefButton } from "@/components/CopyBriefButton";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Начать обучение",
  description: "Выберите тип запроса и отправьте короткий brief в Telegram: взрослый, ребёнок, подросток или business workflow.",
  alternates: { canonical: "/start", languages: { ru: "/start", en: "/en/start" } },
};

const briefs = [
  { meta:"ADULT", title:"Личная программа", href:"/personal", lines:["Цель на ближайшие 1–3 месяца","Какие задачи повторяются сейчас","Какие AI-инструменты уже используете","Online / Phuket · RU / EN"] },
  { meta:"KIDS · 8–13", title:"Для ребёнка", href:"/kids", lines:["Возраст","Что ребёнку интересно","Есть ли опыт с AI","Какой формат проекта мог бы увлечь"] },
  { meta:"TEENS · 14–18", title:"Для подростка", href:"/teens", lines:["Возраст и текущий уровень","Интересы: code / design / science / content / business","Что уже пробовал с AI","Какой portfolio outcome был бы полезен"] },
  { meta:"BUSINESS", title:"Workflow pilot", href:"/business", lines:["Какой процесс хотите улучшить","Кто его выполняет и кто владелец","Как часто он повторяется","Что считается хорошим выходом и что будет при ошибке"] },
];

export default function StartPage(){return <>
  <Header contactHref={site.telegram} alternateHref="/en/start"/>
  <main id="main">
    <section className="contactSection"><div className="shell contactGrid"><div><span className="kicker kickerLight">START · без формы</span><h2>Сначала fit.<br/>Потом программа.</h2><p>Выберите тип запроса ниже и отправьте короткий brief. Для несовершеннолетнего организационный контакт ведёт взрослый.</p><div className="contactButtons"><Link className="button buttonLight" href="/matcher">Подобрать маршрут →</Link><a className="button buttonGhost buttonOnDark" href={site.telegram} target="_blank" rel="noopener noreferrer">Открыть Telegram →</a></div></div><div className="contactOnlyCard"><span className="cardMeta">Что не нужно присылать</span><h3>Минимум данных.</h3><p>Не нужны документы, адрес, школа ребёнка, пароли, API keys, платёжные данные или чувствительная корпоративная информация.</p><small>Scope, стоимость и правила оплаты подтверждаются до любой оплаты.</small></div></div></section>

    <section className="section"><div className="shell"><div className="sectionHead"><span className="kicker">Выберите brief</span><h2>Четыре сообщения, которые экономят лишний созвон.</h2><p className="sectionSub">Не надо отвечать идеально. Эти пункты просто дают достаточно контекста, чтобы предложить адекватный маршрут.</p></div><noscript><div className="briefNoScript"><strong>JavaScript отключён.</strong><p>Кнопки копирования недоступны, но brief можно переписать вручную и сразу открыть Telegram.</p><a className="button buttonGhost" href={site.telegram} target="_blank" rel="noopener noreferrer">Открыть Telegram →</a></div></noscript><div className="programGrid">{briefs.map((b)=><article className="programCard" key={b.meta}><span className="cardMeta">{b.meta}</span><h3>{b.title}</h3><ol className="numberList">{b.lines.map((x)=><li key={x}>{x}</li>)}</ol><div className="briefCardActions"><CopyBriefButton title={b.title} lines={b.lines} locale="ru"/><Link className="textLink" href={b.href}>Посмотреть направление →</Link></div></article>)}</div></div></section>

    <section className="section sectionMuted"><div className="shell splitHead"><div><span className="kicker">Что произойдёт дальше</span><h2>Без скрытого checkout.</h2></div><div><ol className="numberList"><li>Сверяем цель и формат.</li><li>Предлагаем подходящий пакет или более короткий старт.</li><li>Подтверждаем scope, расписание, оплату и правила переноса.</li><li>Только после этого начинается программа.</li></ol></div></div></section>
  </main>
  <Footer/>
</>}
