"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { site } from "@/lib/site";
import { ArrowIcon } from "./ArrowIcon";

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
  const [audience, setAudience] = useState<Audience>(defaultAudience);
  const en = locale === "en";
  const kidsProgram = program.startsWith("kids-");
  const teenProgram = program.startsWith("teens-");
  const youthProgram = kidsProgram || teenProgram;
  const needsAdultConfirmation = youthProgram || audience === "parent" || audience === "teen";
  const base = en ? "/en" : "";

  if (!site.leadFormEnabled) {
    return (
      <div className="contactOnlyCard">
        <span className="cardMeta">{en ? "CONTACT-ONLY LAUNCH" : "CONTACT-ONLY ЗАПУСК"}</span>
        <h3>{en ? "Write directly in Telegram" : "Напишите напрямую в Telegram"}</h3>
        <p>{en ? "The website does not collect application data in the current launch mode. Tell us who the training is for and the result you want." : "В текущем режиме сайт не собирает данные заявок. Напишите, для кого обучение и какой результат хотите получить."}</p>
        <a className="button buttonPrimary buttonWide" href={site.telegram} target="_blank" rel="noreferrer">
          {en ? "Message on Telegram" : "Написать в Telegram"} <ArrowIcon />
        </a>
        {needsAdultConfirmation ? <p className="formNote">{en ? "For minors, the conversation must be started and managed by an adult." : "Для несовершеннолетних переписку начинает и ведёт взрослый."}</p> : null}
      </div>
    );
  }

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
      setAudience(defaultAudience);
      setState("sent");
      setMessage(needsAdultConfirmation
        ? (en ? "Application sent. We will contact you using the adult contact provided." : "Заявка отправлена. Мы свяжемся по указанному контакту взрослого.")
        : (en ? "Application sent. We will contact you using the details provided." : "Заявка отправлена. Мы свяжемся с вами по указанному контакту."));
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
          <select name="audience" value={audience} onChange={(event) => setAudience(event.target.value as Audience)}>
            {kidsProgram ? <option value="parent">{en ? "A parent / guardian" : "Я родитель / опекун"}</option> : null}
            {teenProgram ? <><option value="parent">{en ? "A parent / guardian" : "Я родитель / опекун"}</option><option value="teen">{en ? "Teen program — adult contact" : "Программа 14–18 — контакт взрослого"}</option></> : null}
            {!youthProgram ? <><option value="adult">{en ? "Learning for myself" : "Хочу учиться сам(а)"}</option><option value="parent">{en ? "A parent / guardian" : "Я родитель / опекун"}</option><option value="teen">{en ? "Teen program — adult contact" : "Программа 14–18 — контакт взрослого"}</option><option value="business">{en ? "Team / business" : "Для команды / бизнеса"}</option></> : null}
          </select>
        </label>
      </div>
      <label>
        {en ? "How should we contact you?" : "Как с вами связаться"}
        <input
          name="contact"
          required
          maxLength={120}
          placeholder={needsAdultConfirmation ? (en ? "Adult Telegram, WhatsApp or email" : "Telegram, WhatsApp или email взрослого") : (en ? "Telegram, WhatsApp or email" : "Telegram, WhatsApp или email")}
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

      <label className="consentRow">
        <input type="checkbox" name="privacyConsent" value="yes" required />
        <span>{en ? <>I agree to the processing of this application as described in the <Link href={`${base}/privacy`}>Privacy notice</Link>.</> : <>Я согласен(на) на обработку этой заявки по правилам <Link href="/privacy">конфиденциальности</Link>.</>}</span>
      </label>

      {needsAdultConfirmation ? (
        <label className="consentRow consentYouth">
          <input type="checkbox" name="adultConfirmation" value="yes" required />
          <span>{en ? <>I am an adult organizing the learner&apos;s training and the contact above belongs to an adult. I have read the <Link href={`${base}/safety`}>youth AI safety rules</Link>.</> : <>Я совершеннолетний взрослый, организующий обучение; указанный контакт принадлежит взрослому. Я ознакомился(лась) с <Link href="/safety">правилами безопасности детей и AI</Link>.</>}</span>
        </label>
      ) : null}

      <input name="website" tabIndex={-1} autoComplete="off" className="honeypot" aria-hidden="true" />
      <button className="button buttonPrimary buttonWide" type="submit" disabled={state === "sending"}>
        {state === "sending" ? (en ? "Sending…" : "Отправляем…") : (en ? "Get my program" : "Получить программу")}
      </button>
      <p className="formNote">
        {en ? "For minors, applications and organizational communication use an adult contact only." : "Для несовершеннолетних заявка и организационная коммуникация идут только через взрослого."}
      </p>
      {message ? <p className={state === "sent" ? "formMessage success" : "formMessage error"}>{message}</p> : null}
    </form>
  );
}
