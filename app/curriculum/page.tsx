import type { Metadata } from "next";
import Link from "next/link";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "Программы обучения AI",
  description: "Сравнение программ AI Skill Lab для взрослых, детей 8–13 и подростков 14–18: темы, артефакты, формат и глубина.",
  alternates: { canonical: "/curriculum", languages: { ru: "/curriculum", en: "/en/curriculum" } },
};

const tracks = [
  {
    meta: "ADULT · 1:1",
    title: "Взрослые",
    text: "От уверенной работы с моделями до research workflows, автоматизаций и собственного AI-инструмента.",
    output: "Итог: рабочий процесс, автоматизация, ассистент или mini-product.",
    href: "/personal",
  },
  {
    meta: "KIDS · 8–13",
    title: "Дети",
    text: "Творчество, сильные вопросы, исследование, проверка фактов, цифровые границы и итоговый проект.",
    output: "Итог: проект, который ребёнок может объяснить и презентовать сам.",
    href: "/kids",
  },
  {
    meta: "TEENS · 14–18",
    title: "Подростки",
    text: "AI literacy, research, code-thinking, автоматизации, product thinking и portfolio artifact.",
    output: "Итог: законченный артефакт с понятным личным вкладом.",
    href: "/teens",
  },
];

const adult = [
  ["01", "Диагностика", "Задачи, текущий уровень, ограничения и критерий полезного результата."],
  ["02", "Контекст и спецификация", "Как формулировать требования, критерии качества и формат ответа."],
  ["03", "Исследование", "Источники, сравнение версий, факт-чек и работа с неопределённостью."],
  ["04", "Рабочие шаблоны", "Reusable prompts, инструкции и повторяемые сценарии под реальные задачи."],
  ["05", "Данные и документы", "Как давать модели материал, ограничивать контекст и проверять выводы."],
  ["06", "Automation", "Разбираем повторяемую задачу на шаги и собираем автоматизируемый workflow."],
  ["07", "AI-assistant", "Роли, правила, входы/выходы, failure cases и границы ответственности."],
  ["08", "Проверка качества", "Edge cases, hallucinations, источники, приватность и ручные контрольные точки."],
  ["09", "Сборка проекта", "Интегрируем навыки в один рабочий процесс или инструмент."],
  ["10", "Передача в эксплуатацию", "README, правила использования, улучшения и следующий самостоятельный цикл."],
];

const youth = [
  ["1–2", "Понять инструмент", "Что AI умеет, где ошибается, как задавать контекст и почему ответ надо проверять."],
  ["3–4", "Создать", "Идеи, текст, визуал или интерактив — при сохранении собственного замысла."],
  ["5–6", "Исследовать", "Источники, сравнение фактов, структура презентации и объяснение вывода."],
  ["7–8", "Собрать", "Алгоритмическое мышление, простая логика, прототип, игра или mini-product."],
  ["9–10", "Защитить проект", "Финальная сборка, проверка, личный вклад и самостоятельная презентация результата."],
];

export default function CurriculumPage() {
  return <>
    <Header contactHref="/start" alternateHref="/en/curriculum" />
    <main id="main">
      <section className="hero heroR2"><div className="shell"><div className="eyebrow"><span className="dot" /> CURRICULUM · OUTCOME FIRST</div><h1>Не список кнопок.<br/><span>Траектория до результата.</span></h1><p className="heroLead">Темы адаптируются под уровень и задачу. Ниже — базовая структура, чтобы до старта было понятно, чему именно учимся и что должно появиться на выходе.</p><div className="heroActions"><Link className="button buttonPrimary" href="/pricing">Сравнить пакеты →</Link><Link className="button buttonGhost" href="/start">Подобрать программу →</Link></div></div></section>
      <section className="section"><div className="shell"><div className="sectionHead"><span className="kicker">Три траектории</span><h2>Один принцип: учиться на реальной задаче.</h2></div><div className="programGrid">{tracks.map((track)=><article className="programCard" key={track.title}><span className="cardMeta">{track.meta}</span><h3>{track.title}</h3><p>{track.text}</p><p><b>{track.output}</b></p><Link className="textLink" href={track.href}>Открыть программу →</Link></article>)}</div></div></section>
      <section className="section sectionMuted"><div className="shell"><div className="sectionHead"><span className="kicker">Взрослым · пример ядра на 10 занятий</span><h2>От постановки задачи до рабочего AI-процесса.</h2><p className="sectionSub">Это ориентир, а не жёсткий календарь: если цель техническая или бизнесовая, глубина блоков меняется.</p></div><div className="curriculumList">{adult.map(([n,t,d])=><article key={n}><span>{n}</span><h3>{t}</h3><p>{d}</p></article>)}</div></div></section>
      <section className="section"><div className="shell"><div className="sectionHead"><span className="kicker">Youth · логика 10-занятного маршрута</span><h2>Понять → создать → проверить → объяснить.</h2><p className="sectionSub">Kids и Teens различаются сложностью, самостоятельностью и технической глубиной; организационный контакт для несовершеннолетних идёт через взрослого.</p></div><div className="curriculumList">{youth.map(([n,t,d])=><article key={n}><span>{n}</span><h3>{t}</h3><p>{d}</p></article>)}</div><div className="heroActions"><Link className="button buttonGhost" href="/kids">Дети 8–13 →</Link><Link className="button buttonGhost" href="/teens">Подростки 14–18 →</Link><Link className="button buttonGhost" href="/parents">Родителям →</Link></div></div></section>
      <section className="section sectionInk"><div className="shell splitHead"><div><span className="kicker kickerLight">Как измеряем прогресс</span><h2>Артефакт + объяснение.<br/><em>Не количество промптов.</em></h2></div><div><p>Человек должен уметь поставить задачу, объяснить решение, проверить результат, назвать ограничения и повторить процесс без постоянной подсказки преподавателя.</p><div className="heroActions"><Link className="button buttonLight" href="/projects">Примеры проектов →</Link><Link className="button buttonGhost buttonOnDark" href="/method">Метод обучения →</Link></div></div></div></section>
    </main>
    <Footer />
  </>;
}
