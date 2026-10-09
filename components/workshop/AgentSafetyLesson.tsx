import type { WorkshopLocale } from "./WorkshopShell";
import styles from "./WorkshopShell.module.css";

type CaseItem = {
  label: string;
  title: string;
  body: string;
  note: string;
  source: string;
  sourceLabel: string;
};

const cases: Record<WorkshopLocale, CaseItem[]> = {
  ru: [
    {
      label: "ИНЦИДЕНТ · JUL 2025",
      title: "Replit Agent удалил данные production-базы.",
      body: "Во время эксперимента SaaStr агент Replit удалил данные приложения из базы. Replit позже публично подтвердил проблему: до нового разделения development/production изменения во время разработки могли затронуть production; данные удалось восстановить через rollback.",
      note: "Урок: текстовый запрет вроде «ничего не менять» слабее технической границы, которая физически не даёт агенту писать в production.",
      source: "https://replit.com/blog/doubling-down-on-our-commitment-to-secure-vibe-coding",
      sourceLabel: "Replit · 29.07.2025",
    },
    {
      label: "УЯЗВИМОСТЬ · CVE-2025-32711",
      title: "EchoLeak показал, что входящие данные могут стать инструкцией.",
      body: "Исследователи показали цепочку indirect prompt injection в Microsoft 365 Copilot: специально подготовленное письмо могло попасть в контекст Copilot и привести к утечке данных без клика по письму. Microsoft исправила уязвимость; публично сообщалось, что признаков эксплуатации «в дикой природе» не было.",
      note: "Урок: письмо, веб-страница, документ или комментарий — это недоверенные данные, даже если агент умеет их читать автоматически.",
      source: "https://www.scworld.com/news/microsoft-365-copilot-zero-click-vulnerability-enabled-data-exfiltration",
      sourceLabel: "SC Media · Microsoft CVE-2025-32711",
    },
    {
      label: "АТАКА ОБНАРУЖЕНА · DEC 2025",
      title: "Unit 42 увидела hidden prompts на мошеннических страницах.",
      body: "Unit 42 обнаружила реальные веб-страницы с indirect prompt injection, включая попытку заставить AI-систему проверки рекламы одобрить мошенническое объявление. Исследователи отдельно отмечают: подтверждённого успешного обхода deployed ad-checker в этом кейсе они не видели.",
      note: "Урок: агент, который читает интернет, должен отделять содержимое страницы от команд и не получать лишние права только потому, что «это удобно».",
      source: "https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/",
      sourceLabel: "Palo Alto Networks Unit 42",
    },
  ],
  en: [
    {
      label: "INCIDENT · JUL 2025",
      title: "Replit Agent deleted production-app database data.",
      body: "During a SaaStr experiment, Replit Agent deleted app data from a database. Replit later acknowledged the problem publicly: before its new development/production separation, changes made during development could affect production; the data was restored through rollback.",
      note: "Lesson: a written instruction such as “do not change anything” is weaker than a technical boundary that prevents the agent from writing to production.",
      source: "https://replit.com/blog/doubling-down-on-our-commitment-to-secure-vibe-coding",
      sourceLabel: "Replit · 29 Jul 2025",
    },
    {
      label: "VULNERABILITY · CVE-2025-32711",
      title: "EchoLeak showed that incoming data can become an instruction.",
      body: "Researchers demonstrated an indirect prompt-injection chain in Microsoft 365 Copilot: a crafted email could enter Copilot context and enable data exfiltration without the user clicking the email. Microsoft patched the issue; public reporting said Microsoft had no evidence of in-the-wild exploitation.",
      note: "Lesson: email, webpages, documents and comments are untrusted data even when an agent can read them automatically.",
      source: "https://www.scworld.com/news/microsoft-365-copilot-zero-click-vulnerability-enabled-data-exfiltration",
      sourceLabel: "SC Media · Microsoft CVE-2025-32711",
    },
    {
      label: "ATTACK OBSERVED · DEC 2025",
      title: "Unit 42 found hidden prompts on malicious webpages.",
      body: "Unit 42 observed real webpages carrying indirect prompt injection, including an attempt to make an AI ad-review system approve a scam advertisement. The researchers explicitly noted that they had not confirmed a successful bypass of a deployed ad-checking agent in that case.",
      note: "Lesson: an agent that reads the web must separate page content from commands, and it should not gain extra authority simply because automation is convenient.",
      source: "https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/",
      sourceLabel: "Palo Alto Networks Unit 42",
    },
  ],
};

const rules: Record<WorkshopLocale, Array<[string, string]>> = {
  ru: [
    ["01 · Сначала read-only", "Пусть агент сначала читает, планирует и показывает diff. Право писать выдаётся отдельно и только там, где оно действительно нужно."],
    ["02 · Минимальные права", "Тестовая среда, отдельные аккаунты и ключи, запрет production-доступа по умолчанию. Не давайте агенту больше полномочий, чем требует одна задача."],
    ["03 · Человек перед необратимым действием", "Удаление данных, публикация, отправка сообщения, покупка, платёж или изменение доступа требуют явного подтверждения перед эффектом."],
    ["04 · Данные не равны инструкциям", "Текст из письма, сайта, файла, issue или чата может быть враждебным. Агент не должен превращать найденный контент в новые команды без отдельной проверки."],
    ["05 · Проверка после эффекта", "Нужны журнал действия, проверка результата, способ отката и стоп-условие. «Агент сказал, что всё готово» — не доказательство."],
  ],
  en: [
    ["01 · Start read-only", "Let the agent read, plan and show a diff first. Grant write authority separately and only where one task actually requires it."],
    ["02 · Least privilege", "Use test environments, separate accounts and keys, and no production access by default. Do not give an agent more authority than one task needs."],
    ["03 · Human before irreversible effects", "Data deletion, publishing, sending messages, purchasing, payment or access changes require explicit confirmation before the effect."],
    ["04 · Data is not instruction", "Text from email, webpages, files, issues or chat can be hostile. Retrieved content must not become a new command without a separate trust check."],
    ["05 · Verify after the effect", "Keep an action log, verify the result, define rollback and a stop condition. “The agent said it is done” is not evidence."],
  ],
};

const learnerCases = [
  [
    "Replit: автоматическое действие привело к удалению данных.",
    "Во время эксперимента SaaStr агент Replit удалил данные приложения из базы. Replit подтвердил проблему, а данные впоследствии восстановили.",
    "Для практики используйте учебные или тестовые данные и проверяйте, что именно изменится."
  ],
  [
    "Copilot: письмо содержало скрытые инструкции.",
    "Исследователи описали уязвимость EchoLeak в Microsoft 365 Copilot: специально подготовленное письмо могло привести к утечке данных без клика по письму. Microsoft исправила уязвимость; подтверждённых случаев эксплуатации в открытых источниках не сообщалось.",
    "Письмо или файл могут содержать вредоносные инструкции. Проверяйте, откуда взялся текст."
  ],
  [
    "Unit 42: на веб-страницах нашли скрытые команды.",
    "Исследователи обнаружили веб-страницы с попытками скрыто направлять работу ИИ, включая проверку рекламы. Подтверждённого успешного обхода действующей системы в этом случае не было.",
    "Содержимое сайта — источник информации, а не команда, которую ИИ должен выполнять."
  ]
] as const;
const learnerRules = [
  [
    "01 · Проверяйте источники",
    "Сверяйте важные утверждения с первоисточником и не принимайте уверенный ответ за доказательство."
  ],
  [
    "02 · Берегите личные данные",
    "Не вводите пароли, адреса, платёжные сведения и чужие данные без необходимости и разрешения."
  ],
  [
    "03 · Отличайте данные от указаний",
    "Текст из письма, сайта или файла может содержать команды для ИИ. Не считайте их своими инструкциями."
  ],
  [
    "04 · Согласовывайте важные действия",
    "Перед отправкой, публикацией, удалением или оплатой проверяйте действие и получайте нужное разрешение."
  ],
  [
    "05 · Проверяйте результат",
    "Сравните результат с задачей. Если возможны изменения данных, заранее продумайте способ исправления."
  ]
] as const;

export function AgentSafetyLesson({ locale = "ru", mode = "standard" }: { locale?: WorkshopLocale; mode?: "standard" | "learner" }) {
  if (mode === "learner" && locale === "ru") {
    return (
      <section className={styles.section + " " + styles.agentSafety} id="agent-safety" data-n15-agent-safety="true">
        <div className={styles.sectionHead}><span>ТРИ ПРИМЕРА · ПЯТЬ ПРАВИЛ</span><h2>Безопасность ИИ</h2></div>
        <p className={styles.longCopy}>Безопасность ИИ — это умение проверять источники, беречь данные и не превращать непроверенный ответ в действие без человека.</p>
        <div className={styles.agentSafetyCases}>
          {cases.ru.map((item, index) => (
            <article className={styles.agentSafetyCase} key={item.title}>
              <span>{item.label}</span><h3>{learnerCases[index][0]}</h3><p>{learnerCases[index][1]}</p>
              <strong>{learnerCases[index][2]}</strong>
              <a href={item.source} target="_blank" rel="noopener noreferrer">{item.sourceLabel} ↗</a>
            </article>
          ))}
        </div>
        <p className={styles.longCopy}><strong>Пять правил практики</strong></p>
        <ol className={styles.agentSafetyRules}>{learnerRules.map(([title, body]) => (
          <li key={title}><strong>{title}</strong><p>{body}</p></li>
        ))}</ol>
        <p className={styles.agentSafetyNote}>Примеры различаются: Replit — реальный случай удаления данных; EchoLeak — исправленная уязвимость без подтверждённой эксплуатации в открытых источниках; Unit 42 — обнаруженная попытка скрытого управления ИИ, без подтверждённого успешного обхода.</p>
      </section>
    );
  }

  const en = locale === "en";
  return (
    <section className={`${styles.section} ${styles.agentSafety}`} id="agent-safety">
      <div className={styles.sectionHead}>
        <span>{en ? "SAFE AGENT WORK · 3 CASES + 5 RULES" : "БЕЗОПАСНАЯ РАБОТА С AI-АГЕНТАМИ · 3 КЕЙСА + 5 ПРАВИЛ"}</span>
        <h2>{en ? "Do not trust the plan. Control the effect." : "Не доверять плану. Контролировать эффект."}</h2>
      </div>
      <p className={styles.longCopy}>
        {en
          ? "An AI agent can read, decide and use tools. The risk starts when a plausible answer can turn directly into an external effect. These three documented cases show different failure modes."
          : "AI-агент умеет читать, принимать решения и использовать инструменты. Риск начинается там, где правдоподобный ответ может сразу превратиться во внешний эффект. Эти три документированных кейса показывают разные классы отказа."}
      </p>
      <div className={styles.agentSafetyCases}>
        {cases[locale].map((item) => (
          <article className={styles.agentSafetyCase} key={item.title}>
            <span>{item.label}</span>
            <h3>{item.title}</h3>
            <p>{item.body}</p>
            <strong>{item.note}</strong>
            <a href={item.source} target="_blank" rel="noopener noreferrer">{item.sourceLabel} ↗</a>
          </article>
        ))}
      </div>
      <div className={styles.sectionHead}>
        <span>{en ? "FIVE OPERATING RULES" : "ПЯТЬ РАБОЧИХ ПРАВИЛ"}</span>
        <h2>{en ? "Authority should be explicit." : "Полномочия должны быть явными."}</h2>
      </div>
      <ol className={styles.agentSafetyRules}>
        {rules[locale].map(([title, body]) => (
          <li key={title}><strong>{title}</strong><p>{body}</p></li>
        ))}
      </ol>
      <p className={styles.agentSafetyNote}>
        {en
          ? "The cases are not equivalent: Replit was a real operational incident; EchoLeak was a confirmed vulnerability patched before public disclosure with no known in-the-wild exploitation; the Unit 42 case was an observed malicious injection attempt without confirmed successful bypass of a deployed ad-review agent."
          : "Кейсы не равнозначны: Replit — реальный операционный инцидент; EchoLeak — подтверждённая уязвимость, исправленная до публичного раскрытия, без известной эксплуатации; кейс Unit 42 — обнаруженная вредоносная попытка prompt injection без подтверждённого успешного обхода deployed ad-review агента."}
      </p>
    </section>
  );
}
