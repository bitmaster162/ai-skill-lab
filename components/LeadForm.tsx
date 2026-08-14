"use client";

import { FormEvent, useState } from "react";

type State = "idle" | "sending" | "sent" | "error";

export function LeadForm({ defaultAudience = "adult" }: { defaultAudience?: "adult" | "parent" | "business" }) {
  const [state, setState] = useState<State>("idle");
  const [message, setMessage] = useState("");

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
      if (!response.ok || !result.ok) throw new Error(result.error || "Не удалось отправить заявку");
      form.reset();
      setState("sent");
      setMessage("Заявка отправлена. Мы свяжемся с вами по указанному контакту.");
    } catch (error) {
      setState("error");
      setMessage(error instanceof Error ? error.message : "Не удалось отправить заявку");
    }
  }

  return (
    <form className="leadForm" onSubmit={onSubmit}>
      <div className="formRow">
        <label>
          Ваше имя
          <input name="name" required maxLength={80} autoComplete="name" placeholder="Имя" />
        </label>
        <label>
          Кто вы
          <select name="audience" defaultValue={defaultAudience}>
            <option value="adult">Хочу учиться сам(а)</option>
            <option value="parent">Я родитель</option>
            <option value="business">Для команды / бизнеса</option>
          </select>
        </label>
      </div>
      <label>
        Как с вами связаться
        <input
          name="contact"
          required
          maxLength={120}
          placeholder="Telegram, WhatsApp или email"
          autoComplete="email"
        />
      </label>
      <label>
        Что хотите получить от обучения
        <textarea name="goal" maxLength={600} rows={4} placeholder="Например: научиться создавать AI-агентов, автоматизировать работу или подобрать программу ребёнку" />
      </label>
      <input name="website" tabIndex={-1} autoComplete="off" className="honeypot" aria-hidden="true" />
      <button className="button buttonPrimary buttonWide" type="submit" disabled={state === "sending"}>
        {state === "sending" ? "Отправляем…" : "Получить программу"}
      </button>
      <p className="formNote">
        Для детской программы указывайте контакт родителя, а не ребёнка.
      </p>
      {message ? <p className={state === "sent" ? "formMessage success" : "formMessage error"}>{message}</p> : null}
    </form>
  );
}
