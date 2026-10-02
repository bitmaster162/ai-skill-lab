"use client";

import Link from "next/link";
import { diagnosticCtaSummary, introCall, introWhatsappHref } from "@/lib/e1_4";
import type { WorkshopLocale } from "@/lib/commercial";

declare global {
  interface Window {
    va?: (command: string, payload: { name: string; data?: Record<string, string> }) => void;
  }
}

function track(channel: "whatsapp" | "telegram") {
  window.va?.("event", { name: "intro_call_click", data: { channel } });
}

export function IntroCallCta({ locale = "ru", showDiagnostic = true }: { locale?: WorkshopLocale; showDiagnostic?: boolean }) {
  const en = locale === "en";
  const start = en ? "/en/start#application-form" : "/start#application-form";
  return <div className={`e14EntryStart ${showDiagnostic ? "" : "e14EntryStartSingle"}`} data-e14-entry>
    <article className="e14EntryCard">
      <span className="e14EntryMeta">{en ? "FIRST STEP" : "ПЕРВЫЙ ШАГ"}</span>
      <p className="e14EntryCopy">{introCall.freeMeta[locale]}</p>
      <div className="e14EntryActions">
        <a className="workshopButton workshopButtonPrimary" data-intro-call-channel="whatsapp" href={introWhatsappHref(locale)} target="_blank" rel="noopener noreferrer" onClick={() => track("whatsapp")}>{introCall.label[locale]}</a>
        <a className="workshopButton workshopButtonSecondary" data-intro-call-channel="telegram" href={introCall.telegramUrl} target="_blank" rel="noopener noreferrer" onClick={() => track("telegram")}>Telegram →</a>
      </div>
    </article>
    {showDiagnostic ? <article className="e14EntryCard e14DiagnosticCard">
      <span className="e14EntryMeta">{en ? "SECOND STEP" : "ВТОРОЙ ШАГ"}</span>
      <p className="e14DiagnosticLine" data-e14-diagnostic>{diagnosticCtaSummary(locale)}</p>
      <Link className="workshopButton workshopButtonSecondary" href={start}>{en ? "Discuss diagnostic →" : "Обсудить диагностику →"}</Link>
    </article> : null}
  </div>;
}
