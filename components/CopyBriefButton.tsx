"use client";

import { useState } from "react";

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

export function CopyBriefButton({ title, lines, locale = "ru" }: CopyBriefButtonProps) {
  const [copied, setCopied] = useState(false);
  const isEn = locale === "en";
  const text = [
    isEn ? "AI Skill Lab — brief" : "AI Skill Lab — запрос",
    `${isEn ? "Route" : "Маршрут"}: ${title}`,
    ...lines.map((line, index) => `${index + 1}. ${line}: `),
  ].join("\n");

  return (
    <button
      className="button buttonSmall buttonGhost briefCopyButton"
      type="button"
      onClick={async () => {
        const ok = await copyText(text);
        setCopied(ok);
        if (ok) window.setTimeout(() => setCopied(false), 1800);
      }}
      aria-live="polite"
    >
      {copied ? (isEn ? "Copied ✓" : "Скопировано ✓") : (isEn ? "Copy brief" : "Скопировать brief")}
    </button>
  );
}
