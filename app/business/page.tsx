import type { Metadata } from "next";
import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { PilotSimulator } from "@/components/PilotSimulator";

export const metadata: Metadata = {
  title: "AI для бизнеса",
  description: "Практическое обучение AI и workflow-pilot для предпринимателей и команд: карта процесса, один проверяемый prototype, QA, ownership и handoff.",
  alternates: { canonical: "/business", languages: { ru: "/business", en: "/en/business" } },
  twitter: { card: "summary_large_image", title: "AI для бизнеса", description: "Практическое обучение AI и workflow-pilot для предпринимателей и команд: карта процесса, один проверяемый prototype, QA, ownership и handoff.", images: ["/opengraph-image"] },
};

const offers = [
  ["01", "Workflow audit", "Карта повторяемых задач, bottlenecks, границ данных и точек возможного AI-внедрения."],
  ["02", "Обучение команды", "Ролевые сессии на реальных документах, процессах и решениях конкретной команды."],
  ["03", "Implementation pilot", "Один выбранный workflow: prototype + QA + ownership + operating rules + handoff."],
];

const pilot = [
  ["01", "Map", "Фиксируем текущий процесс, входы/выходы, владельца, частоту, ручные проверки и цену ошибки."],
  ["02", "Select", "Выбираем один workflow с понятной пользой и ограниченным blast radius — не пытаемся автоматизировать компанию за неделю."],
  ["03", "Prototype & test", "Собираем рабочую версию, проверяем edge cases, качество, данные, fallback и человеческие контрольные точки."],
  ["04", "Handoff", "Документируем ownership, operating rules, ограничения, критерии проверки и следующий список улучшений."],
];

const good = [
  "повторяемая knowledge-work задача с понятным входом и выходом",
  "документы, research, классификация, черновики или подготовка решений с human review",
  "есть владелец процесса и можно описать, что считается хорошим результатом",
  "можно начать с ограниченного пилота без автономного доступа к критичным действиям",
];

const bad = [
  "нет владельца процесса или никто не готов проверять результат",
  "задача требует полностью автономного safety-critical решения",
  "нет права использовать необходимые данные или неясны privacy boundaries",
  "ожидание — заменить людей одной кнопкой без изменения процесса и контроля",
];

export default function Page() {
  return <>
    <Header contactHref="/start" alternateHref="/en/business" />
    <main id="main">
      <section className="teenHero"><div className="shell teenHeroGrid"><div><span className="eyebrow">Founders · teams · operators</span><h1>Не «добавить AI».<br/><span>Изменить один процесс.</span></h1><p>Начинаем с повторяемой работы, качества и рисков. Потом выбираем один workflow, который можно проверить, передать владельцу и улучшать дальше.</p><div className="heroActions"><Link className="button buttonLight" href="/start">Обсудить business scope</Link><Link className="button buttonGhost buttonOnDark" href="/method">Метод →</Link></div></div></div></section>

      <section className="section"><div className="shell"><span className="kicker">Форматы</span><h2>Три способа начать</h2><div className="programGrid">{offers.map(([n,t,x])=><article className="programCard" key={n}><span className="cardIndex">{n}</span><div className="cardSpacer"/><h3>{t}</h3><p>{x}</p></article>)}</div></div></section>

      <section className="section sectionMuted"><div className="shell"><div className="sectionHead"><span className="kicker">Implementation pilot</span><h2>Один workflow → проверяемый operating model.</h2><p className="sectionSub">Пилот специально ограничен. Цель — доказать, что процесс можно улучшить безопасно и повторяемо, а не показать эффектный demo, который никто не сможет поддерживать.</p></div><div className="steps">{pilot.map(([n,t,d])=><article key={n}><span>{n}</span><h3>{t}</h3><p>{d}</p></article>)}</div></div></section>

      <section className="section sectionInk" id="pilot-simulator"><div className="shell"><div className="sectionHead sectionHeadLight"><span className="kicker kickerLight">AI Pilot Simulator</span><h2>Сначала ограничить процесс.<br/>Потом влюбляться в demo.</h2><p>Выберите типовой workflow. Эта deterministic local-демонстрация показывает candidate boundary, роль AI, human checkpoint, success signal и условие, при котором пилот надо остановить.</p></div><PilotSimulator/></div></section>

      <section className="section"><div className="shell parentGrid"><div className="parentCard"><span className="kicker">Хороший кандидат</span><h2>Где пилот имеет смысл</h2><ul className="checkList checkDark">{good.map((x)=><li key={x}>{x}</li>)}</ul></div><div className="parentCard parentDark"><span className="kicker kickerLight">Стоп-сигналы</span><h2>Где сначала нужен другой разбор</h2><ul className="checkList">{bad.map((x)=><li key={x}>{x}</li>)}</ul></div></div></section>

      <section className="section sectionInk"><div className="shell splitHead"><div><span className="kicker kickerLight">Что остаётся после пилота</span><h2>Артефакты,<br/><em>а не AI-театр.</em></h2></div><div><p>Current-state map · candidate backlog · prototype / automation · test cases · human checkpoints · privacy/data boundaries · owner & fallback · operating notes.</p><div className="heroActions"><Link className="button buttonLight" href="/projects">Примеры форматов →</Link></div></div></div></section>


      <section className="section sectionMuted"><div className="shell"><div className="sectionHead"><span className="kicker">Decision gate</span><h2>Ship · Revise · Stop.</h2><p className="sectionSub">До сборки фиксируем, что будет считаться приемлемым результатом: качество выхода, обязательный human review, допустимые failure modes, data boundaries, fallback и владелец процесса. После теста решение принимается по этим критериям, а не по эффектности demo.</p></div><div className="steps"><article><span>01</span><h3>Ship</h3><p>Критерии проверки пройдены, owner принимает процесс и понятно, кто контролирует работу дальше.</p></article><article><span>02</span><h3>Revise</h3><p>Ценность есть, но обнаружены ограниченные проблемы качества, данных, UX или operating rules, которые можно исправить следующим циклом.</p></article><article><span>03</span><h3>Stop</h3><p>Риск, отсутствие владельца, слабое качество или ограничения данных делают внедрение хуже, чем текущий процесс. Пилот останавливается без обязательства «внедрить AI».</p></article></div></div></section>

      <section className="section"><div className="shell splitHead"><div><span className="kicker">Первое сообщение</span><h2>Достаточно шести пунктов.</h2></div><div><ol className="numberList"><li>Какой процесс хотите улучшить.</li><li>Кто его выполняет и кто владелец.</li><li>Как часто он повторяется.</li><li>Какие входные данные используются.</li><li>Что считается хорошим выходом.</li><li>Что произойдёт, если AI ошибётся.</li></ol><div className="heroActions"><Link className="button buttonPrimary" href="/start">Подготовить brief →</Link></div></div></div></section>
    </main>
    <Footer />
  </>;
}
