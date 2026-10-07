"use client";

import { useEffect } from "react";

type PublicEvent =
  | "lead_submit_ok"
  | "lead_submit_error"
  | "cal_click"
  | "telegram_click"
  | "whatsapp_click"
  | "line_click"
  | "email_click";

const leadEvents = new Set<PublicEvent>(["lead_submit_ok", "lead_submit_error"]);

function classifyContact(href: string): PublicEvent | null {
  if (href.startsWith("mailto:")) return "email_click";
  try {
    const url = new URL(href, window.location.origin);
    const host = url.hostname.toLowerCase();
    if (host === "cal.com" || host.endsWith(".cal.com")) return "cal_click";
    if (host === "t.me" || host.endsWith(".t.me")) return "telegram_click";
    if (host === "wa.me" || host.endsWith(".whatsapp.com")) return "whatsapp_click";
    if (host === "line.me" || host.endsWith(".line.me")) return "line_click";
  } catch {
    return null;
  }
  return null;
}

function pagePath() {
  return window.location.pathname.replace(/\/+$/, "") || "/";
}

function pageLocale(): "ru" | "en" {
  return document.documentElement.lang === "en" ? "en" : "ru";
}

function sendPublicEvent(event: PublicEvent) {
  void fetch("/api/event", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "omit",
    cache: "no-store",
    keepalive: true,
    body: JSON.stringify({ event, page: pagePath(), locale: pageLocale() }),
  }).catch(() => undefined);
}

export function PublicEventTracker() {
  useEffect(() => {
    const onClick = (event: MouseEvent) => {
      const target = event.target as Element | null;
      const anchor = target?.closest?.("a[href]") as HTMLAnchorElement | null;
      if (!anchor) return;
      const tracked = classifyContact(anchor.getAttribute("href") || "");
      if (tracked) sendPublicEvent(tracked);
    };
    const onLead = (event: Event) => {
      const tracked = (event as CustomEvent<{ event?: PublicEvent }>).detail?.event;
      if (tracked && leadEvents.has(tracked)) sendPublicEvent(tracked);
    };
    document.addEventListener("click", onClick);
    window.addEventListener("asl:lead-event", onLead);
    return () => {
      document.removeEventListener("click", onClick);
      window.removeEventListener("asl:lead-event", onLead);
    };
  }, []);
  return null;
}
