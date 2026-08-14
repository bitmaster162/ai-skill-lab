"use client";

import { FormEvent, useState } from "react";

type State = "idle" | "sending" | "sent" | "error";
type Audience = "adult" | "parent" | "teen" | "business";
type Locale = "ru" | "en";

export function LeadForm({
  defaultAudience = "adult",
  locale = "ru",
  program = "",
}: {
  defaultAudience?: Audience;
  locale?: Locale;
  program?: string;
}) {
  const [state, setState] = useState<State>("idle");
  const [message, setMessage] = useState("");
  const en = locale === "en";

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState("sending");
    setMessage("");

    const form = event.currentTarget;
    const data = Object.fromEntries(new FormData(form).entries());

    try {
      const response = await fetch("/api/lead", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      const result = (await response.json()) as { ok?: boolean; error?: string };
      if (!response.ok || !result.ok) throw new Error(result.error || (en ? "Could not send the application" : "Не удалось отправить заявку"));
      form.reset();
      setState("sent");
      setMessage(en ? "Application sent. We will contact you using the details provided." : "Заявка отправлена. Мы свяжемся с вами по указанному контакту.");
    } catch (error) {
      setState("error");
      setMessage(error instanceof Error ? error.message : (en ? "Could not send the application" : "Не удалось отправить заявку"));
    }
  }

  return (
    <form className="leadForm" onSubmit={onSubmit}>
      <input type="hidden" name="locale" value={locale} />
      <input type="hidden" name="program" value={program} />
      <div className="formRow">
        <label>
          {en ? "Your name" : "Ваше имя"}
          <input name="name" required maxLength={80} autoComplete="name" placeholder={en ? "Name" : "Имя"} />
        </label>
        <label>
          {en ? "I am" : "Кто вы"}
          <select name="audience" defaultValue={defaultAudience}>
            <option value="adult">{en ? "Learning for myself" : "Хочу учиться сам(а)"}</option>
            <option value="parent">{en ? "A parent / guardian" : "Я родитель"}</option>
            <option value="teen">{en ? "Teen program — adult contact" : "Программа 14–18 — контакт взрослого"}</option>
            <option value="business">{en ? "Team / business" : "Для команды / бизнеса"}</option>
          </select>
        </label>
      </div>
      <label>
        {en ? "How should we contact you?" : "Как с вами связаться"}
        <input
          name="contact"
          required
          maxLength={120}
          placeholder={en ? "Telegram, WhatsApp or email" : "Telegram, WhatsApp или email"}
          autoComplete="email"
        />
      </label>
      <label>
        {en ? "What outcome do you want?" : "Что хотите получить от обучения"}
        <textarea
          name="goal"
          maxLength={600}
          rows={4}
          placeholder={en ? "For example: build AI agents, automate work, or choose a program for my child" : "Например: научиться создавать AI-агентов, автоматизировать работу или подобрать программу ребёнку"}
        />
      </label>
      <input name="website" tabIndex={-1} autoComplete="off" className="honeypot" aria-hidden="true" />
      <button className="button buttonPrimary buttonWide" type="submit" disabled={state === "sending"}>
        {state === "sending" ? (en ? "Sending…" : "Отправляем…") : (en ? "Get my program" : "Получить программу")}
      </button>
      <p className="formNote">
        {en ? "For minors, provide an adult's contact details only." : "Для детских и подростковых программ указывайте контакт взрослого, а не ребёнка."}
      </p>
      {message ? <p className={state === "sent" ? "formMessage success" : "formMessage error"}>{message}</p> : null}
    </form>
  );
}
