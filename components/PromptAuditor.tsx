"use client";

import { useState } from "react";
import type { WorkshopLocale } from "@/components/workshop/WorkshopShell";

type AuditResult = {
  status: "ok";
  score: number;
  improved: string;
  explanation: string;
  requestId?: string;
};

const copy = {
  ru: {
    title: "ИИ Проверка промпта",
    intro: "Вставьте рабочий запрос к LLM — ИИ оценит его по 10-балльной шкале и предложит улучшенный вариант с пояснением.",
    privacy: "Запускается только по кнопке. Текст передаётся настроенной модели через OpenRouter; AI Skill Lab его не сохраняет. Не вставляйте пароли, ключи и приватные данные.",
    placeholder: "Например: Составь план исследования рынка для нового B2B ИИ-продукта и укажи, какие выводы нужно проверить отдельно.",
    run: "Проверить промпт",
    running: "Проверяем…",
    score: "ИИ-оценка",
    why: "Пояснение",
    improved: "Улучшенный вариант",
    note: "Это автоматическая оценка, а не универсальный стандарт качества. Проверьте улучшенный промпт перед использованием.",
    secret: "Похоже, в тексте есть секрет или ключ. Удалите его: такие данные не передаются модели.",
    rate: "Лимит ИИ-проверок временно исчерпан. Попробуйте позже.",
    unavailable: "Проверка промпта сейчас недоступен. Исходный текст никуда дополнительно не сохранялся.",
    copy: "Скопировать улучшенный промпт",
    copied: "Скопировано",
    copyError: "Не удалось скопировать",
  },
  en: {
    title: "AI Prompt Auditor",
    intro: "Paste a working LLM request — AI scores it on a 10-point scale and returns an improved version with an explanation.",
    privacy: "Runs only after you press the button. The text is sent to the configured model through OpenRouter; AI Skill Lab does not store it. Do not paste passwords, keys or private data.",
    placeholder: "For example: Build a market-research plan for a new B2B AI product and flag which conclusions need separate verification.",
    run: "Audit prompt",
    running: "Auditing…",
    score: "AI score",
    why: "Explanation",
    improved: "Improved version",
    note: "This is an automated assessment, not a universal quality standard. Review the improved prompt before using it.",
    secret: "The text appears to contain a secret or credential. Remove it; those values are not sent to the model.",
    rate: "The AI audit limit is temporarily reached. Try again later.",
    unavailable: "Prompt Auditor is unavailable right now. The original text was not stored by AI Skill Lab.",
    copy: "Copy improved prompt",
    copied: "Copied",
    copyError: "Copy failed",
  },
} as const;

export function PromptAuditor({ locale = "ru" }: { locale?: WorkshopLocale }) {
  const t = copy[locale];
  const [prompt, setPrompt] = useState("");
  const [state, setState] = useState<"idle"|"loading"|"ready"|"secret"|"rate"|"error">("idle");
  const [result, setResult] = useState<AuditResult|null>(null);
  const [copyState, setCopyState] = useState<"idle"|"done"|"error">("idle");

  async function runAudit() {
    const value = prompt.trim();
    if (!value || state === "loading") return;
    setState("loading"); setResult(null); setCopyState("idle");
    try {
      const response = await fetch("/api/route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: "prompt_audit", locale, prompt: value }),
      });
      const body = await response.json().catch(() => null);
      if (body?.status === "secret_detected") { setState("secret"); return; }
      if (response.status === 429) { setState("rate"); return; }
      if (
        response.ok &&
        body?.status === "ok" &&
        Number.isInteger(body.score) &&
        body.score >= 1 &&
        body.score <= 10 &&
        typeof body.improved === "string" &&
        typeof body.explanation === "string"
      ) {
        setResult(body as AuditResult);
        setState("ready");
        return;
      }
      setState("error");
    } catch {
      setState("error");
    }
  }

  async function copyImproved() {
    if (!result) return;
    try { await navigator.clipboard.writeText(result.improved); setCopyState("done"); }
    catch { setCopyState("error"); }
  }

  const message = state === "secret" ? t.secret : state === "rate" ? t.rate : state === "error" ? t.unavailable : "";

  return <section className="matcherShell" data-prompt-auditor>
    <div className="matcherPrivacy statusDot">{t.privacy}</div>
    <section className="matcherQuestion">
      <span className="cardMeta">AI PROMPT AUDITOR</span>
      <h2>{t.title}</h2>
      <p>{t.intro}</p>
      <textarea className="matcherGoalInput" value={prompt} maxLength={2000} rows={5} placeholder={t.placeholder} onChange={(event)=>{setPrompt(event.target.value);setState("idle");setResult(null);setCopyState("idle")}} />
      <button className="button buttonPrimary" type="button" disabled={!prompt.trim() || state === "loading"} onClick={runAudit}>{state === "loading" ? t.running : t.run}</button>
    </section>
    <section className="matcherResult" aria-live="polite">
      {message ? <p className="matcherEmpty">{message}</p> : result ? <>
        <div className="matcherResultTop"><div><span className="cardMeta">{t.score}</span><p className="promptAuditScore">{result.score}/10</p></div></div>
        <div className="matcherReason"><b>{t.why}</b><p>{result.explanation}</p></div>
        <div className="matcherReason"><b>{t.improved}</b><p>{result.improved}</p></div>
        <p className="matcherNote">{t.note}</p>
        <button type="button" className="button buttonGhost" onClick={copyImproved}>{copyState === "done" ? t.copied : copyState === "error" ? t.copyError : t.copy}</button>
      </> : null}
    </section>
  </section>;
}
