"use client";

import { useEffect, useRef } from "react";

type Locale = "ru" | "en";

type LabCommandProps = { locale?: Locale };

const copy = {
  ru: {
    open: "Открыть Lab Command",
    close: "Закрыть Lab Command",
    title: "AI SKILL LAB / COMMAND",
    hint: "CTRL / ⌘ + K",
    esc: "ESC TO CLOSE",
    items: [
      ["01", "Proof Lab", "/proof", "METHOD"],
      ["02", "Project Studio", "/projects", "BUILD"],
      ["03", "Pilot Simulator", "/business#pilot-simulator", "BUSINESS"],
      ["04", "Program Matcher", "/matcher", "MATCH"],
      ["05", "AI Challenge", "/challenge", "SYSTEM"],
      ["06", "Build Log", "/build", "PROVENANCE"],
      ["07", "Start", "/start", "START"],
    ],
  },
  en: {
    open: "Open Lab Command",
    close: "Close Lab Command",
    title: "AI SKILL LAB / COMMAND",
    hint: "CTRL / ⌘ + K",
    esc: "ESC TO CLOSE",
    items: [
      ["01", "Proof Lab", "/en/proof", "METHOD"],
      ["02", "Project Studio", "/en/projects", "BUILD"],
      ["03", "Pilot Simulator", "/en/business#pilot-simulator", "BUSINESS"],
      ["04", "Program Matcher", "/en/matcher", "MATCH"],
      ["05", "AI Challenge", "/en/challenge", "SYSTEM"],
      ["06", "Build Log", "/en/build", "PROVENANCE"],
      ["07", "Start", "/en/start", "START"],
    ],
  },
} as const;

export function LabCommand({ locale = "ru" }: LabCommandProps) {
  const t = copy[locale];
  const dialogRef = useRef<HTMLDialogElement>(null);

  const open = () => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) dialog.showModal();
  };

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        open();
      }
    };
    const external = [...document.querySelectorAll<HTMLElement>("[data-lab-command-open]")].filter((el) => !el.classList.contains("labCommandTrigger"));
    external.forEach((el) => el.addEventListener("click", open));
    window.addEventListener("keydown", onKey);
    return () => {
      external.forEach((el) => el.removeEventListener("click", open));
      window.removeEventListener("keydown", onKey);
    };
  }, []);

  return (
    <>
      <button
        className="langSwitch labCommandTrigger"
        type="button"
        aria-label={t.open}
        aria-haspopup="dialog"
        aria-controls="lab-command"
        aria-keyshortcuts="Control+K Meta+K"
        onClick={open}
      >
        ⌘K
      </button>
      <dialog className="labDialog" id="lab-command" ref={dialogRef} aria-label={t.open}>
        <div className="proofConsole">
          <div className="proofConsoleTop">
            <span>{t.title}</span>
            <button className="langSwitch" type="button" aria-label={t.close} onClick={() => dialogRef.current?.close()}>ESC</button>
          </div>
          <div className="proofConsoleBody labCommandBody">
            {t.items.map(([index, label, href, meta]) => (
              <p key={href}>
                <span>{index}</span>
                <a href={href}>{label}</a>
                <strong>{meta}</strong>
              </p>
            ))}
          </div>
          <div className="proofConsoleFoot"><span>{t.hint}</span><i /><span>{t.esc}</span></div>
        </div>
      </dialog>
    </>
  );
}
