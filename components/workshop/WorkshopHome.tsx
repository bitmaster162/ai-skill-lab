import Link from "next/link";
import type { CSSProperties } from "react";
import { commercialFacts, sessionDurationMinutes } from "@/lib/commercial";
import { WorkshopShell, type WorkshopLocale } from "./WorkshopShell";
import styles from "./WorkshopShell.module.css";

export function WorkshopHome({ locale = "ru" }: { locale?: WorkshopLocale }) {
  const en = locale === "en";
  const p = (ru: string) => en ? `/en${ru}` : ru;
  const adult = commercialFacts.tracks.adult;
  const family = commercialFacts.family;
  const studioHref = en ? "/en/studio" : "/studio";
  const routes = en ? [
    ["ADULTS", "Build a working AI process", "Research, writing, code and automation around your real work.", "/en/personal", "#8ab4ff"],
    ["TEENS", "Turn curiosity into portfolio", "Research, code and product thinking with a finished artifact.", "/en/teens", "#5ee0c0"],
    ["KIDS", "Create without outsourcing the thinking", "A project-based route with adult contact and privacy by default.", "/en/kids", "#c9a3ff"],
    ["BUSINESS", "Change one repeatable workflow", "Map, test, verify and hand off one bounded implementation.", "/en/business", "#f5f7f9"],
  ] : [
    ["ВЗРОСЛЫЕ", "Собрать рабочий AI-процесс", "Research, тексты, код и автоматизация на ваших реальных задачах.", "/personal", "#8ab4ff"],
    ["ПОДРОСТКИ", "Превратить интерес в портфолио", "Research, код и product thinking с законченной работой.", "/teens", "#5ee0c0"],
    ["ДЕТИ", "Создавать, не отдавая мышление AI", "Проектный маршрут, контакт взрослого и приватность по умолчанию.", "/kids", "#c9a3ff"],
    ["БИЗНЕС", "Изменить один повторяемый процесс", "Карта, тест, проверка и handoff одного ограниченного внедрения.", "/business", "#f5f7f9"],
  ];
  return (
    <WorkshopShell locale={locale} alternateHref={en ? "/" : "/en"}>
      <main id="main">
        <section className={styles.hero}>
          <div className={styles.heroCopy}>
            <span className={styles.eyebrow}>AI SKILL LAB · 1:1 · ONLINE / PHUKET</span>
            <h1>{en ? <>Learn AI so the <em>capability stays with you.</em></> : <>Освойте AI так, чтобы <em>результат остался у вас.</em></>}</h1>
            <p>{en ? "Practical learning, hands-on building and one-workflow business implementation. You understand the system, verify it and can keep using it." : "Практическое обучение, сборка AI-проектов и внедрение одного бизнес-процесса. Вы понимаете систему, проверяете её и можете пользоваться дальше."}</p>
            <div className={styles.heroActions}><Link className="workshopButton workshopButtonPrimary" href={p("/start")}>{en ? "Find my route →" : "Подобрать маршрут →"}</Link><Link className="workshopButton workshopButtonSecondary" href={p("/proof")}>Proof Lab</Link></div>
            <div className={styles.signalRow}><span>1:1</span><span>{sessionDurationMinutes} {en ? "minutes" : "минут"}</span><span>{en ? "Real project" : "Реальный проект"}</span><span>Human review</span></div>
          </div>
          <aside className={styles.heroPanel}>
            <span>{en ? "THE WORKSHOP LOOP" : "ЦИКЛ МАСТЕРСКОЙ"}</span>
            <ol><li><b>01</b>{en ? "Define the outcome" : "Определить результат"}</li><li><b>02</b>{en ? "Build on real work" : "Собрать на реальной задаче"}</li><li><b>03</b>{en ? "Verify the output" : "Проверить результат"}</li><li><b>04</b>{en ? "Keep the capability" : "Забрать навык с собой"}</li></ol>
          </aside>
        </section>
        <section className={styles.section}>
          <div className={styles.sectionHead}><span>{en ? "CHOOSE A TRACK" : "ВЫБЕРИТЕ ТРЕК"}</span><h2>{en ? "Different buyers. One standard: a result you can explain." : "Разные аудитории. Один стандарт: результат, который можно объяснить."}</h2></div>
          <div className={styles.trackGrid}>{routes.map(([tag,title,text,href,color]) => <Link className={styles.trackCard} data-track={tag} style={{"--track": color} as CSSProperties} href={href} key={href}><span>{tag}</span><h3>{title}</h3><p>{text}</p><b>{en ? "Open track →" : "Открыть трек →"}</b></Link>)}</div>
        </section>
        <section className={styles.darkBand}>
          <div><span>{en ? "BUILD / BUSINESS" : "BUILD / БИЗНЕС"}</span><h2>{en ? "Not AI theatre. One bounded system with ownership." : "Не AI-театр. Одна ограниченная система с владельцем результата."}</h2><p>{en ? "AI Studio for an assistant, automation or product — built with explicit scope, verification and handoff." : "Studio для ассистента, автоматизации или продукта — с явным scope, проверкой и handoff."}</p></div>
          <div className={styles.bandSteps}><span>MAP</span><span>BUILD</span><span>VERIFY</span><span>HANDOFF</span></div>
          <div className={styles.bandActions}><Link className="workshopButton workshopButtonLight" href={p("/business")}>{en ? "See business formats →" : "Посмотреть бизнес-форматы →"}</Link><Link className="workshopButton workshopButtonSecondary" href={studioHref}>{en ? "Open Studio →" : "Открыть Studio →"}</Link></div>
        </section>
        <section className={`${styles.section} ${styles.paper}`}>
          <div className={styles.sectionHead}><span>{en ? "CLEAR START" : "ПОНЯТНЫЙ СТАРТ"}</span><h2>{en ? "Personal packages stay transparent." : "Персональные пакеты остаются прозрачными."}</h2></div>
          <div className={styles.priceGrid}>{adult.map(plan => <article className={styles.priceCard} key={plan.id}><span>{plan.name}</span><strong>{plan.price}</strong><b>{en ? plan.sessions_en : plan.sessions_ru}</b><p>{en ? plan.summary_en : plan.summary_ru}</p></article>)}<article className={styles.priceCard}><span>{family.name}</span><strong>{family.price}</strong><b>{en ? family.sessions_en : family.sessions_ru}</b><p>{en ? family.summary_en : family.summary_ru}</p></article></div>
          <div className={styles.sectionActions}><Link className="workshopButton workshopButtonDark" href={p("/pricing")}>{en ? "All prices and formats →" : "Все цены и форматы →"}</Link></div>
        </section>
        <section className={styles.proofBand}><div><span>{en ? "VERIFIABLE PRACTICE" : "ПРОВЕРЯЕМЫЙ ПОДХОД"}</span><h2>{en ? "Sources, tests, human gates and fallback remain visible." : "Источники, тесты, human gates и fallback остаются видимыми."}</h2></div><p>{en ? "Proof stays — after the offer, not instead of it." : "Proof остаётся — после оффера, а не вместо него."}</p><Link href={p("/proof")}>{en ? "Open Proof Lab →" : "Открыть Proof Lab →"}</Link></section>
        <section className={styles.finalCta}><span>{en ? "FIRST STEP" : "ПЕРВЫЙ ШАГ"}</span><h2>{en ? "Describe the task, level and outcome." : "Опишите задачу, уровень и желаемый результат."}</h2><Link className="workshopButton workshopButtonPrimary" href={p("/start")}>{en ? "Start →" : "Начать →"}</Link></section>
      </main>
    </WorkshopShell>
  );
}
