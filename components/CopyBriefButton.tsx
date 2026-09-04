"use client";

import { useEffect, useState } from "react";

type CopyBriefButtonProps = {
  title: string;
  lines: string[];
  locale?: "ru" | "en";
};

async function copyText(text: string) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    const ok = document.execCommand("copy");
    area.remove();
    return ok;
  }
}

function getSameOriginSource() {
  if (typeof window === "undefined" || typeof document === "undefined" || !document.referrer) return "";
  try {
    const referrer = new URL(document.referrer);
    if (referrer.origin !== window.location.origin) return "";
    const path = referrer.pathname.replace(/\/+$/, "") || "/";
    if (path === "/start" || path === "/en/start") return "";
    return path;
  } catch {
    return "";
  }
}

export function CopyBriefButton({ title, lines, locale = "ru" }: CopyBriefButtonProps) {
  const [copyState, setCopyState] = useState<"idle" | "done" | "error">("idle");
  const [source, setSource] = useState("");
  const isEn = locale === "en";

  useEffect(() => {
    setSource(getSameOriginSource());
  }, []);

  const text = [
    isEn ? "AI Skill Lab — brief" : "AI Skill Lab — запрос",
    `${isEn ? "Route" : "Маршрут"}: ${title}`,
    ...(source ? [`${isEn ? "Source" : "Источник"}: ${source}`] : []),
    ...lines.map((line, index) => `${index + 1}. ${line}: `),
  ].join("\n");
  const telegramHref = `https://t.me/BiTFormer?text=${encodeURIComponent(text)}`;

  return (
    <div className="briefActions">
      <button
        className="workshopButton workshopButtonSecondary briefCopy"
        type="button"
        onClick={async () => {
          const ok = await copyText(text);
          setCopyState(ok ? "done" : "error");
          window.setTimeout(() => setCopyState("idle"), 1800);
        }}
        aria-live="polite"
      >
        {copyState === "done"
          ? (isEn ? "Copied ✓" : "Скопировано ✓")
          : copyState === "error"
            ? (isEn ? "Copy failed" : "Не удалось скопировать")
            : (isEn ? "Copy brief" : "Скопировать brief")}
      </button>
      <a
        className="workshopButton workshopButtonPrimary briefSendLink"
        href={telegramHref}
        target="_blank"
        rel="noopener noreferrer"
      >
        {isEn ? "Send in Telegram →" : "Отправить в Telegram →"}
      </a>
    </div>
  );
}
