import Link from "next/link";
import { commercialFacts, sessionDurationMinutes } from "@/lib/commercial";
import { WorkshopShell, type WorkshopLocale } from "./WorkshopShell";
import styles from "./WorkshopShell.module.css";

export function WorkshopFamily({ locale = "ru" }: { locale?: WorkshopLocale }) {
  const en = locale === "en";
  const start = en ? "/en/start" : "/start";
  const included = en ? [
    ["01", "12 learner sessions", "The full age-appropriate Kids or Teens route, built around one learner and one finished project."],
    ["02", "2 parent sessions", "Understand the learner's work, the model boundary and the criteria used to review the project."],
    ["03", "Household rules", "Write down allowed services, prohibited data, own-work boundaries and when an adult must step in."],
    ["04", "Final presentation", "The learner presents the project, checks the result and explains their own contribution."],
  ] : [
    ["01", "12 занятий с учеником", "Полная возрастная программа Kids или Teens вокруг одного ученика и одного законченного проекта."],
    ["02", "2 занятия с родителем", "Разобраться в работе ребёнка, границе модели и критериях проверки итогового проекта."],
    ["03", "Домашние правила", "Зафиксировать разрешённые сервисы, запрещённые данные, границу собственной работы и участие взрослого."],
    ["04", "Финальная защита", "Ученик показывает проект, проверяет результат и объясняет собственный вклад."],
  ];
  const principles = en ? [
    ["ONE LEARNER", "Family Concierge is one learner's program. A second learner is a separately scoped pair format."],
    ["UNDERSTANDING, NOT SURVEILLANCE", "Parent sessions create a shared language for review without replacing the learner's agency."],
    ["WRITTEN WITH YOUR FAMILY", "Household rules are built around your context, not copied from a universal template."],
  ] : [
    ["ОДИН УЧЕНИК", "Family Concierge — программа для одного ученика. Второй ученик оформляется как отдельно согласованный парный формат."],
    ["ПОНИМАНИЕ, НЕ НАДЗОР", "Родительские занятия создают общий язык проверки, не подменяя самостоятельность ребёнка."],
    ["ПРАВИЛА ВМЕСТЕ С СЕМЬЁЙ", "Домашние правила собираются под ваш контекст, а не копируются из универсального шаблона."],
  ];
  const family = commercialFacts.family;
  return (
    <WorkshopShell locale={locale} alternateHref={en ? "/family" : "/en/family"}>
      <main id="main">
        <section className={styles.familyHero}>
          <div className={styles.familyHeroCopy}>
            <span className={styles.familyEyebrow}>{en ? "FAMILY FORMAT · ONE LEARNER" : "СЕМЕЙНЫЙ ФОРМАТ · ОДИН УЧЕНИК"}</span>
            <h1>{en ? <>The child learns.<br/><em>The household sets the rules.</em></> : <>Учится ребёнок.<br/><em>Правила заводит семья.</em></>}</h1>
            <p className={styles.familyLead}>{en ? "Twelve sessions with the learner, two with a parent, and written household rules for using AI that stay with you after the program ends." : "Двенадцать занятий с учеником, два — с родителем, и письменные домашние правила обращения с AI, которые остаются у вас после программы."}</p>
            <div className={styles.heroActions}>
              <Link className="workshopButton workshopButtonPrimary" href={start}>{en ? "Discuss the family route →" : "Обсудить семейный маршрут →"}</Link>
              <a className="workshopButton workshopButtonSecondary" href="#included">{en ? "What is included ↓" : "Что входит ↓"}</a>
            </div>
          </div>
          <aside className={styles.familyPrice} aria-label={en ? "Family Concierge price and format" : "Цена и формат Family Concierge"}>
            <span>{family.name}</span>
            <strong>{family.price}</strong>
            <b>{en ? family.sessions_en : family.sessions_ru}</b>
            <small>{en ? `ONE LEARNER · 14 × ${sessionDurationMinutes} MINUTES` : `ОДИН УЧЕНИК · 14 × ${sessionDurationMinutes} МИНУТ`}</small>
          </aside>
        </section>
        <section className={`${styles.section} ${styles.familyPanel}`} id="included">
          <div className={styles.sectionHead}><span>{en ? "INCLUDED" : "ЧТО ВХОДИТ"}</span><h2>{en ? "Learning, a parent loop and rules that remain usable." : "Обучение, parent loop и правила, которыми можно пользоваться дальше."}</h2></div>
          <div className={styles.familyIncludedGrid}>{included.map(([number,title,text]) => <article className={styles.familyItem} key={number}><span>{number}</span><h3>{title}</h3><p>{text}</p></article>)}</div>
        </section>
        <section className={`${styles.section} ${styles.paper} ${styles.familyHonesty}`}>
          <div className={styles.sectionHead}><span>{en ? "HONEST BOUNDARY" : "ЧЕСТНАЯ ГРАНИЦА"}</span><h2>{en ? "A family system without taking the work away from the learner." : "Семейная система без подмены работы ученика."}</h2></div>
          <div className={styles.familyRuleGrid}>{principles.map(([title,text]) => <article className={styles.familyRule} key={title}><strong>{title}</strong><p>{text}</p></article>)}</div>
        </section>
        <section className={`${styles.darkBand} ${styles.familyAdult}`}>
          <div><span>{en ? "ADULT CONTACT" : "КОНТАКТ ВЗРОСЛОГО"}</span><h2>{en ? "Organizational communication stays with an adult." : "Организационную переписку ведёт взрослый."}</h2><p>{en ? "Send the learner's age range, interests and desired outcome. Do not send school, address, passwords, payment data or the child's own contact details." : "Достаточно возраста, интересов и желаемого результата. Не присылайте школу, адрес, пароли, платёжные данные или личные контакты ребёнка."}</p></div>
          <Link className="workshopButton workshopButtonLight" href={start}>{en ? "Open Start →" : "Перейти к Start →"}</Link>
        </section>
        <section className={styles.finalCta}><span>{en ? "FIRST BRIEF" : "ПЕРВЫЙ BRIEF"}</span><h2>{en ? "Age range + interest + outcome is enough." : "Возраст + интерес + результат — достаточно."}</h2><Link className="workshopButton workshopButtonPrimary" href={start}>{en ? "Discuss Family Concierge →" : "Обсудить Family Concierge →"}</Link></section>
      </main>
    </WorkshopShell>
  );
}
