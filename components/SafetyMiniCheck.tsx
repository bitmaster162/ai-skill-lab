"use client";

import { useState } from "react";

type Locale = "ru" | "en";
type Question = { id: string; prompt: string; options: [string, string]; correct: "a" | "b" };

const QUESTIONS: Record<Locale, Question[]> = {
  ru: [
    { id: "under13", prompt: "Если ChatGPT используется с ребёнком младше 13 лет в образовательном контексте, кто проводит фактическое взаимодействие с сервисом?", options: ["Взрослый", "Ребёнок самостоятельно"], correct: "a" },
    { id: "teen", prompt: "Что требуется пользователю 13–18 лет по текущей справке OpenAI?", options: ["Разрешение родителя или законного представителя", "Никакого отдельного условия"], correct: "a" },
    { id: "contact", prompt: "Кто ведёт заявку, расписание, оплату и организационные сообщения для несовершеннолетнего?", options: ["Взрослый", "Ребёнок через личный мессенджер"], correct: "a" },
    { id: "privacy", prompt: "Что не нужно вводить в AI-задания без необходимости?", options: ["Домашний адрес, документы, пароли и приватные переписки", "Только контекст, необходимый для задачи"], correct: "a" },
    { id: "verify", prompt: "Что делать, если AI отвечает уверенно?", options: ["Считать ответ правильным", "Проверить утверждения и источники и исправить результат при необходимости"], correct: "b" },
  ],
  en: [
    { id: "under13", prompt: "If ChatGPT is used with a child under 13 in an education context, who conducts the actual interaction with the service?", options: ["An adult", "The child independently"], correct: "a" },
    { id: "teen", prompt: "What do users ages 13–18 need under OpenAI's current guidance?", options: ["Permission from a parent or legal guardian", "No additional condition"], correct: "a" },
    { id: "contact", prompt: "Who handles applications, scheduling, payment and organizational communication for a minor?", options: ["An adult", "The child through a personal messenger account"], correct: "a" },
    { id: "privacy", prompt: "What should not be entered into AI assignments unless genuinely needed?", options: ["Home addresses, identity documents, passwords and private conversations", "Only the context needed for the task"], correct: "a" },
    { id: "verify", prompt: "What should you do when AI sounds confident?", options: ["Assume the answer is correct", "Verify claims and sources and correct the output when needed"], correct: "b" },
  ],
};

export function SafetyMiniCheck({ locale = "ru" }: { locale?: Locale }) {
  const questions = QUESTIONS[locale];
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [checked, setChecked] = useState(false);

  const answered = questions.filter((q) => answers[q.id]).length;
  const matches = questions.filter((q) => answers[q.id] === q.correct).length;
  const result = !checked
    ? ""
    : answered < questions.length
      ? (locale === "en" ? "Answer all five questions before checking." : "Ответьте на все пять вопросов перед проверкой.")
      : matches === questions.length
        ? (locale === "en" ? "5/5 answers match the current rules on this page." : "5/5 ответов совпадают с текущими правилами этой страницы.")
        : (locale === "en" ? `${matches}/5 answers match. Review the highlighted rules on this page.` : `${matches}/5 ответов совпадают. Пересмотрите выделенные правила на этой странице.`);

  return <section className="policyCallout safetyQuiz" data-safety-quiz data-locale={locale}>
    <div className="safetyQuizHead">
      <span>{locale === "en" ? "MINI-CHECK · LOCAL ONLY" : "МИНИ-ТЕСТ · ТОЛЬКО В БРАУЗЕРЕ"}</span>
      <h2>{locale === "en" ? "Do these five safety rules match your understanding?" : "Совпадают ли эти пять правил с вашим пониманием?"}</h2>
      <p>{locale === "en" ? "Nothing is sent or stored. This checks only your understanding of the rules on this page; it is not a safety certification." : "Ничего не отправляется и не сохраняется. Тест проверяет только понимание правил этой страницы и не является сертификатом безопасности."}</p>
    </div>
    <div className="safetyQuizQuestions">
      {questions.map((q) => {
        const state = checked ? (!answers[q.id] ? "missing" : answers[q.id] === q.correct ? "match" : "review") : undefined;
        return <fieldset key={q.id} className="safetyQuizQuestion" data-safety-question data-state={state}>
          <legend>{q.prompt}</legend>
          {q.options.map((option, optionIndex) => {
            const value = optionIndex === 0 ? "a" : "b";
            return <label key={value}>
              <input
                type="radio"
                name={`safety-${q.id}`}
                value={value}
                checked={answers[q.id] === value}
                onChange={() => { setAnswers((prev) => ({ ...prev, [q.id]: value })); setChecked(false); }}
              />
              <span>{option}</span>
            </label>;
          })}
        </fieldset>;
      })}
    </div>
    <div className="safetyQuizFooter">
      <button className="button buttonGhost" type="button" onClick={() => setChecked(true)}>{locale === "en" ? "Check answers" : "Проверить ответы"}</button>
      <p aria-live="polite" className="safetyQuizResult">{result}</p>
    </div>
  </section>;
}
