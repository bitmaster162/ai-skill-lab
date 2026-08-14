"use client";

import { useMemo, useState } from "react";
import Link from "next/link";

export type MatcherLocale = "ru" | "en";

type Audience = "adult" | "kids" | "teens" | "business";
type Goal = "research" | "create" | "automate" | "team";
type Depth = "intro" | "core" | "deep";

const copy = {
  ru: {
    private: "Локально в браузере · ничего не отправляется",
    audience: "1. Для кого маршрут?",
    goal: "2. Что важнее всего?",
    depth: "3. Насколько глубоко хотите зайти?",
    audienceOptions: [
      ["adult", "Взрослый"], ["kids", "Ребёнок 8–13"], ["teens", "Подросток 14–18"], ["business", "Команда / бизнес"],
    ],
    goalOptions: [
      ["research", "Исследования и решения"], ["create", "Контент и проекты"], ["automate", "Автоматизация / агенты"], ["team", "Рабочий процесс команды"],
    ],
    depthOptions: [
      ["intro", "Понять и попробовать"], ["core", "Собрать рабочую систему"], ["deep", "Сделать сильный финальный проект"],
    ],
    resultLabel: "Стартовая рекомендация",
    noResult: "Выберите по одному варианту в каждом блоке. Рекомендация считается только на этой странице и никуда не отправляется.",
    why: "Почему этот маршрут",
    note: "Это не автоматическое подтверждение fit. Перед оплатой вручную сверяем цель, уровень, расписание и scope.",
    track: "Посмотреть направление →",
    start: "Отправить brief →",
    reset: "Сбросить",
  },
  en: {
    private: "Local in your browser · nothing is sent",
    audience: "1. Who is the route for?",
    goal: "2. What matters most?",
    depth: "3. How deep do you want to go?",
    audienceOptions: [
      ["adult", "Adult"], ["kids", "Child 8–13"], ["teens", "Teen 14–18"], ["business", "Team / business"],
    ],
    goalOptions: [
      ["research", "Research and decisions"], ["create", "Content and projects"], ["automate", "Automation / agents"], ["team", "Team workflow"],
    ],
    depthOptions: [
      ["intro", "Understand and try"], ["core", "Build a working system"], ["deep", "Ship a strong final project"],
    ],
    resultLabel: "Starting recommendation",
    noResult: "Choose one option in each block. The recommendation is calculated only on this page and is not sent anywhere.",
    why: "Why this route",
    note: "This is not an automatic fit approval. Goal, level, schedule and scope are confirmed manually before payment.",
    track: "View the track →",
    start: "Send a brief →",
    reset: "Reset",
  },
} as const;

const plans = {
  adult: {
    intro: { ru:["Start", "$390", "4 занятия"], en:["Start", "$390", "4 sessions"] },
    core: { ru:["Personal", "$890", "10 занятий"], en:["Personal", "$890", "10 sessions"] },
    deep: { ru:["Intensive", "$1,290", "12 занятий + проект"], en:["Intensive", "$1,290", "12 sessions + project"] },
    path: "/personal",
  },
  kids: {
    intro: { ru:["Mini", "$290", "4 занятия"], en:["Mini", "$290", "4 sessions"] },
    core: { ru:["Creator", "$890", "10 занятий"], en:["Creator", "$890", "10 sessions"] },
    deep: { ru:["Studio", "$1,190", "12 занятий"], en:["Studio", "$1,190", "12 sessions"] },
    path: "/kids",
  },
  teens: {
    intro: { ru:["Explorer", "$490", "6 занятий"], en:["Explorer", "$490", "6 sessions"] },
    core: { ru:["Portfolio", "$890", "10 занятий"], en:["Portfolio", "$890", "10 sessions"] },
    deep: { ru:["Builder", "$1,290", "12 занятий"], en:["Builder", "$1,290", "12 sessions"] },
    path: "/teens",
  },
} as const;

const reasons = {
  ru: {
    research: "Нужен переносимый навык постановки задачи, поиска источников и проверки выводов.",
    create: "Фокус на собственном замысле, итерациях и понятном финальном артефакте.",
    automate: "Маршрут должен дойти до повторяемого workflow, прототипа ассистента или автоматизации.",
    team: "Нужны владелец процесса, критерий качества, fallback и проверяемый pilot scope.",
    business: "Для команды сначала выбирается один повторяемый процесс и тестируется ограниченный пилот. Стоимость зависит от scope, поэтому фиксированный пакет здесь был бы выдумкой.",
  },
  en: {
    research: "The transferable skill is task definition, source work and verification of conclusions.",
    create: "The focus is original intent, iteration and a clear finished artifact.",
    automate: "The route should reach a repeatable workflow, assistant prototype or automation.",
    team: "A team route needs a process owner, quality criterion, fallback and a testable pilot scope.",
    business: "For a team, one repeatable process is selected first and tested as a bounded pilot. Pricing depends on scope, so a fixed package here would be invented precision.",
  },
} as const;

export function ProgramMatcher({ locale = "ru" }: { locale?: MatcherLocale }) {
  const t = copy[locale];
  const [audience, setAudience] = useState<Audience | null>(null);
  const [goal, setGoal] = useState<Goal | null>(null);
  const [depth, setDepth] = useState<Depth | null>(null);
  const base = locale === "en" ? "/en" : "";

  const result = useMemo(() => {
    if (!audience || !goal || !depth) return null;
    if (audience === "business") {
      return {
        title: locale === "ru" ? "Business workflow pilot" : "Business workflow pilot",
        price: locale === "ru" ? "Custom scope" : "Custom scope",
        length: locale === "ru" ? "1 процесс → ограниченный пилот" : "1 process → bounded pilot",
        reason: reasons[locale].business,
        path: `${base}/business`,
      };
    }
    const audienceKey = audience as Exclude<Audience, "business">;
    const depthKey = depth as Depth;
    const goalKey = goal as Goal;
    const p = plans[audienceKey][depthKey][locale];
    return {
      title: p[0], price: p[1], length: p[2], reason: reasons[locale][goalKey], path: `${base}${plans[audienceKey].path}`,
    };
  }, [audience, goal, depth, locale, base]);

  const choose = <T extends string>(value: T, current: T | null, setter: (v:T)=>void, label: string) => (
    <button type="button" className={`matcherOption ${current===value ? "isSelected" : ""}`} aria-pressed={current===value} onClick={() => setter(value)}>{label}</button>
  );

  return <div className="matcherShell">
    <div className="matcherPrivacy"><span>●</span>{t.private}</div>
    <section className="matcherQuestion" aria-labelledby="matcher-audience"><h2 id="matcher-audience">{t.audience}</h2><div className="matcherOptions">{t.audienceOptions.map(([v,l]) => choose(v as Audience,audience,setAudience,l))}</div></section>
    <section className="matcherQuestion" aria-labelledby="matcher-goal"><h2 id="matcher-goal">{t.goal}</h2><div className="matcherOptions">{t.goalOptions.map(([v,l]) => choose(v as Goal,goal,setGoal,l))}</div></section>
    <section className="matcherQuestion" aria-labelledby="matcher-depth"><h2 id="matcher-depth">{t.depth}</h2><div className="matcherOptions">{t.depthOptions.map(([v,l]) => choose(v as Depth,depth,setDepth,l))}</div></section>
    <section className="matcherResult" aria-live="polite">
      <span className="cardMeta">{t.resultLabel}</span>
      {!result ? <p className="matcherEmpty">{t.noResult}</p> : <>
        <div className="matcherResultTop"><div><h2>{result.title}</h2><p>{result.length}</p></div><strong>{result.price}</strong></div>
        <div className="matcherReason"><b>{t.why}</b><p>{result.reason}</p></div>
        <p className="matcherNote">{t.note}</p>
        <div className="heroActions"><Link className="button buttonPrimary" href={result.path}>{t.track}</Link><Link className="button buttonGhost" href={`${base}/start`}>{t.start}</Link><button type="button" className="matcherReset" onClick={() => {setAudience(null);setGoal(null);setDepth(null)}}>{t.reset}</button></div>
      </>}
    </section>
  </div>;
}
