import type { Metadata } from "next";
import Link from "next/link";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "FAQ",
  description: "Ответы о формате AI Skill Lab: 1-на-1, online / Phuket, цены, проекты, детские программы и contact-only старт.",
  alternates: { canonical: "/faq", languages: { ru: "/faq", en: "/en/faq" } },
};

const items = [
  ["Это записанный курс?", "Нет. Базовый формат — персональные занятия 1-на-1 вокруг конкретной задачи и итогового артефакта."],
  ["Можно заниматься полностью online?", "Да. Online — основной географически независимый формат. В Phuket очные сессии возможны по предварительной договорённости."],
  ["Как выбрать пакет?", "Сначала короткий brief: кому обучение, цель, текущий уровень, язык и формат. После этого определяется подходящая глубина, а не наоборот."],
  ["Есть ли оплата прямо на сайте?", "Нет. Публичный сайт работает в contact-only режиме: без checkout и собственной формы сбора заявок."],
  ["Что будет результатом обучения?", "Не сертификат ради сертификата, а законченный проект, workflow, исследование, прототип или другая работа, которую можно объяснить и проверить."],
  ["Как устроено обучение детей?", "Для несовершеннолетних организационный контакт ведёт взрослый. Возрастные правила конкретных AI-сервисов проверяются до использования."],
  ["AI делает домашнюю работу за ученика?", "Нет. Метод строится вокруг постановки задачи, проверки, итераций и способности объяснить собственный вклад."],
  ["Можно ли собрать программу под бизнес-задачу?", "Да. Для взрослых и команд маршрут может строиться вокруг research, automation, AI-assistant, workflow или внутреннего mini-product."],
  ["Что происходит после сообщения в Telegram?", "Сначала сверяем цель и формат. Затем предлагаем подходящий пакет или более короткий старт, письменно подтверждаем scope, расписание, оплату и правила переноса — и только после этого начинается программа."],
  ["Когда и на каких условиях происходит оплата?", "Оплата принимается только после согласования конкретной услуги. До неё должны быть зафиксированы финальная стоимость и scope, способ оплаты и реквизиты поставщика, а также правила переноса, отмены и возврата."],
  ["Сколько длится одно занятие?", "Пакет фиксирует количество занятий, но не скрытую стандартную длительность. Точная длительность одной сессии и расписание согласуются и фиксируются до оплаты как часть конкретного scope."],
];

export default function FaqPage() {
  return <><Header contactHref="/start" alternateHref="/en/faq"/><main id="main"><section className="hero heroR2"><div className="shell"><div className="eyebrow"><span className="dot"/> FAQ · BEFORE YOU START</div><h1>Сначала вопросы.<br/><span>Потом пакет.</span></h1><p className="heroLead">Короткие ответы на то, что имеет смысл понять до первого разговора.</p><div className="heroActions"><Link className="button buttonPrimary" href="/start">Обсудить задачу →</Link><Link className="textLink" href="/pricing">Стоимость →</Link></div></div></section><section className="section"><div className="shell"><div className="faqGrid"><div className="sectionHead stickyHead"><span className="kicker">FAQ</span><h2>11 коротких ответов</h2></div><div className="faqList">{items.map(([q,a])=><details key={q}><summary>{q}<span>+</span></summary><p>{a}</p></details>)}</div></div></div></section></main><Footer/></>;
}
