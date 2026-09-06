"use client";

import { useMemo, useState, useSyncExternalStore } from "react";

type Locale = "ru" | "en";

const WEEKS_PER_MONTH = 52 / 12;

const copy = {
  ru: {
    local: "Локальный сценарий · данные не отправляются",
    team: "Людей в процессе",
    weeklyHours: "Рутины на человека в неделю",
    rate: "Оценочная стоимость часа",
    recoverable: "Предполагаемая доля высвобождаемого времени",
    monthlyRoutine: "Текущая рутина",
    recoverableHours: "Потенциально высвобождается",
    grossValue: "Валовая стоимость высвобождённой ёмкости",
    hoursMonth: "ч / мес",
    perHour: "/ч",
    perMonth: "/ мес",
    action: "Открыть Start для обсуждения →",
    note: "Это сценарий чувствительности, а не прогноз и не обещание экономии. Формула не учитывает стоимость внедрения, модели/API, интеграций, контроля качества, ошибок, налогов или то, будет ли высвобождённое время реально монетизировано.",
    formula: "Формула: люди × часы рутины/нед × 52/12 × выбранная доля высвобождения × стоимость часа.",
    briefTitle: "AI Skill Lab — Business capacity scenario",
  },
  en: {
    local: "Local scenario · no data is sent",
    team: "People in the process",
    weeklyHours: "Routine hours per person / week",
    rate: "Estimated hourly value",
    recoverable: "Assumed recoverable share of routine time",
    monthlyRoutine: "Current routine load",
    recoverableHours: "Potentially recoverable",
    grossValue: "Gross value of recovered capacity",
    hoursMonth: "h / month",
    perHour: "/h",
    perMonth: "/ month",
    action: "Open Start to discuss the scenario →",
    note: "This is a sensitivity scenario, not a forecast or savings guarantee. It excludes implementation, model/API, integration, QA, error, tax costs and whether recovered time can actually be monetized.",
    formula: "Formula: people × routine hours/week × 52/12 × selected recoverable share × hourly value.",
    briefTitle: "AI Skill Lab — Business capacity scenario",
  },
} as const;

const subscribeHydration = () => () => {};
const clientReady = () => true;
const serverReady = () => false;

export function BusinessValueCalculator({ locale = "ru" }: { locale?: Locale }) {
  const t = copy[locale];
  const interactive = useSyncExternalStore(subscribeHydration, clientReady, serverReady);
  const [team, setTeam] = useState(3);
  const [weeklyHours, setWeeklyHours] = useState(10);
  const [rate, setRate] = useState(25);
  const [recoverable, setRecoverable] = useState(30);

  const values = useMemo(() => {
    const monthlyRoutine = team * weeklyHours * WEEKS_PER_MONTH;
    const recoverableHours = monthlyRoutine * (recoverable / 100);
    const grossValue = recoverableHours * rate;
    return { monthlyRoutine, recoverableHours, grossValue };
  }, [team, weeklyHours, rate, recoverable]);

  const number = (value: number) => new Intl.NumberFormat(locale === "ru" ? "ru-RU" : "en-US", {
    maximumFractionDigits: Math.abs(value) > 0 && Math.abs(value) < 10 ? 1 : 0,
  }).format(value);
  const money = (value: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);

  const brief = [
    t.briefTitle,
    `${t.team}: ${team}`,
    `${t.weeklyHours}: ${weeklyHours}`,
    `${t.rate}: $${rate}${t.perHour}`,
    `${t.recoverable}: ${recoverable}%`,
    `${t.recoverableHours}: ~${number(values.recoverableHours)} ${t.hoursMonth}`,
    `${t.grossValue}: ~${money(values.grossValue)} ${t.perMonth}`,
    locale === "ru" ? "Статус: scenario only · не прогноз · требуется human validation процесса." : "Status: scenario only · not a forecast · process assumptions require human validation.",
  ].join("\n");

  const startHref = locale === "ru" ? "/start#business-brief" : "/en/start#business-brief";

  return <div className="businessValue" data-business-value data-locale={locale}>
    <div className="businessValueSignal"><span aria-hidden="true">●</span>{t.local}</div>
    <div className="businessValueInputs">
      <label htmlFor="bv-team"><span>{t.team}</span><strong>{team}</strong><input disabled={!interactive} id="bv-team" type="range" min="1" max="30" value={team} onChange={e => setTeam(Number(e.target.value))}/></label>
      <label htmlFor="bv-hours"><span>{t.weeklyHours}</span><strong>{weeklyHours} {locale === "ru" ? "ч" : "h"}</strong><input disabled={!interactive} id="bv-hours" type="range" min="1" max="40" value={weeklyHours} onChange={e => setWeeklyHours(Number(e.target.value))}/></label>
      <label htmlFor="bv-rate"><span>{t.rate}</span><strong>${rate}{t.perHour}</strong><input disabled={!interactive} id="bv-rate" type="range" min="10" max="200" step="5" value={rate} onChange={e => setRate(Number(e.target.value))}/></label>
      <label htmlFor="bv-recoverable"><span>{t.recoverable}</span><strong>{recoverable}%</strong><input disabled={!interactive} id="bv-recoverable" type="range" min="10" max="80" step="5" value={recoverable} onChange={e => setRecoverable(Number(e.target.value))}/></label>
    </div>
    <div className="businessValueResults" aria-live="polite">
      <article><span>{t.monthlyRoutine}</span><strong data-bv-result="monthlyRoutine">~{number(values.monthlyRoutine)} {t.hoursMonth}</strong></article>
      <article><span>{t.recoverableHours}</span><strong data-bv-result="recoverableHours">~{number(values.recoverableHours)} {t.hoursMonth}</strong></article>
      <article><span>{t.grossValue}</span><strong data-bv-result="grossValue">~{money(values.grossValue)} {t.perMonth}</strong></article>
    </div>
    <p className="businessValueFormula">{t.formula}</p>
    <p className="businessValueNote">{t.note}</p>
    <details className="businessValueBrief"><summary>{locale === "ru" ? "Текст для brief — скопируйте вручную" : "Brief text — copy manually"}</summary><pre data-bv-brief>{interactive ? brief : ""}</pre></details>
    <noscript><p>{locale === "ru" ? "JavaScript выключен: показан исходный сценарий; поля недоступны." : "JavaScript is disabled: the initial scenario is shown; inputs are unavailable."}</p></noscript>
    <div className="heroActions"><a className="button buttonPrimary" href={startHref}>{t.action}</a></div>
  </div>;
}
