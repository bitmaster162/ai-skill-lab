import Link from "next/link";
import { CopyBriefButton } from "@/components/CopyBriefButton";
import { sessionDurationMinutes } from "@/lib/commercial";
import { ChannelLinks } from "./ChannelLinks";
import { WorkshopShell, type WorkshopLocale } from "./WorkshopShell";
import styles from "./WorkshopShell.module.css";

const copy = {
  ru: [
    { meta: "ADULT", title: "Личная программа", href: "/personal", lines: ["Цель на ближайшие 1–3 месяца", "Какие задачи повторяются сейчас", "Какие AI-инструменты уже используете", "Online / Phuket · RU / EN"] },
    { meta: "KIDS · 8–13", title: "Для ребёнка", href: "/kids", lines: ["Возраст", "Что ребёнку интересно", "Есть ли опыт с AI", "Какой проект мог бы увлечь"] },
    { meta: "TEENS · 14–18", title: "Для подростка", href: "/teens", lines: ["Возраст и текущий уровень", "Интересы: code / design / science / content / business", "Что уже пробовал с AI", "Какой portfolio outcome был бы полезен"] },
    { meta: "AI STUDIO", title: "AI Studio / build", href: "/studio", lines: ["Что хотите собрать или изменить", "Что происходит сейчас / что уже есть", "Кто будет пользоваться и кто владелец результата", "Что считается готовым / где ошибка будет критична"] },
    { meta: "BUSINESS", title: "Workflow pilot", href: "/business", lines: ["Какой процесс хотите улучшить", "Кто его выполняет и кто владелец", "Как часто он повторяется", "Какие входные данные используются", "Что считается хорошим выходом", "Что произойдёт, если AI ошибётся"] },
  ],
  en: [
    { meta: "ADULT", title: "Personal program", href: "/en/personal", lines: ["Goal for the next 1–3 months", "Which tasks repeat today", "Which AI tools you already use", "Online / Phuket · RU / EN"] },
    { meta: "KIDS · 8–13", title: "For a child", href: "/en/kids", lines: ["Age", "What the learner is interested in", "Any prior AI experience", "What kind of project might be motivating"] },
    { meta: "TEENS · 14–18", title: "For a teen", href: "/en/teens", lines: ["Age and current level", "Interests: code / design / science / content / business", "What they already tried with AI", "Which portfolio outcome would be useful"] },
    { meta: "AI STUDIO", title: "AI Studio / build", href: "/en/studio", lines: ["What you want to build or change", "What happens today / what already exists", "Who will use it and who owns the outcome", "What counts as done / where failure would be costly"] },
    { meta: "BUSINESS", title: "Workflow pilot", href: "/en/business", lines: ["Which process you want to improve", "Who performs and owns it", "How often it repeats", "Which inputs it uses", "What a good output looks like", "What happens if AI is wrong"] },
  ],
} as const;

export function WorkshopStart({ locale = "ru" }: { locale?: WorkshopLocale }) {
  const en = locale === "en";
  const briefs = copy[locale];
  return (
    <WorkshopShell locale={locale} alternateHref={en ? "/start" : "/en/start"} contactHref="#contact-channels">
      <main id="main">
        <section className={styles.startHero}><span>{en ? "START · CONTACT-ONLY" : "START · БЕЗ ФОРМЫ"}</span><h1>{en ? <>Fit first.<br/><em>Program second.</em></> : <>Сначала fit.<br/><em>Потом программа.</em></>}</h1><p>{en ? `A session is ${sessionDurationMinutes} minutes. Choose a channel or copy a short brief; for a minor, coordination stays with an adult.` : `Сессия длится ${sessionDurationMinutes} минут. Выберите канал или скопируйте короткий brief; для несовершеннолетнего контакт ведёт взрослый.`}</p></section>
        <section className={styles.section}><div className={styles.sectionHead}><span>{en ? "CONTACT" : "КОНТАКТ"}</span><h2>{en ? "Four direct routes. No website form." : "Четыре прямых канала. Без формы на сайте."}</h2></div><ChannelLinks locale={locale}/><p className={styles.dataNote}>{en ? "Do not send identity documents, passwords, API keys, payment data or a child’s direct contact." : "Не присылайте документы, пароли, API keys, платёжные данные или прямой контакт ребёнка."}</p></section>
        <section className={`${styles.section} ${styles.panelSection}`}><div className={styles.sectionHead}><span>{en ? "CHOOSE A BRIEF" : "ВЫБЕРИТЕ BRIEF"}</span><h2>{en ? "Five messages that remove an unnecessary call." : "Пять сообщений, которые экономят лишний созвон."}</h2></div><noscript><p>{en ? "Copy the fields manually and use one of the channels above." : "Перепишите пункты вручную и используйте один из каналов выше."}</p></noscript><div className={styles.briefGrid}>{briefs.map((brief, index) => <article className={styles.briefCard} key={brief.meta} id={index === 3 ? "studio-brief" : index === 4 ? "business-brief" : undefined}><span>{brief.meta}</span><h3>{brief.title}</h3><ol>{brief.lines.map(line => <li key={line}>{line}</li>)}</ol><CopyBriefButton title={brief.title} lines={[...brief.lines]} locale={locale}/><Link href={brief.href}>{en ? "View track →" : "Посмотреть направление →"}</Link></article>)}</div></section>
        <section className={`${styles.section} ${styles.paper}`}><div className={styles.sectionHead}><span>{en ? "NEXT" : "ДАЛЬШЕ"}</span><h2>{en ? "No hidden checkout." : "Без скрытого checkout."}</h2></div><ol className={styles.nextSteps}><li>{en ? "Confirm the goal and format." : "Сверяем цель и формат."}</li><li>{en ? "Recommend a package or smaller start." : "Предлагаем пакет или более короткий старт."}</li><li>{en ? "Confirm scope, schedule, payment and rescheduling in writing." : "Письменно подтверждаем scope, расписание, оплату и переносы."}</li><li>{en ? "Only then does the program start." : "Только после этого начинается программа."}</li></ol></section>
      </main>
    </WorkshopShell>
  );
}
