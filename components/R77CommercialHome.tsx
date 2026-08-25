import Link from "next/link";
import styles from "./R77CommercialHome.module.css";

export type R77Locale = "ru" | "en";

export function R77CommercialHome({ locale = "ru" }: { locale?: R77Locale }) {
  const ru = locale === "ru";
  const p = (ruPath: string, enPath?: string) => (ru ? ruPath : (enPath ?? `/en${ruPath}`));

  const tracks = ru
    ? [
        ["01 · LEARN", "Освоить AI на своих задачах", "1-на-1 для взрослых, подростков и детей: research, тексты, код, автоматизация и фактчекинг.", "/personal", "Выбрать обучение →"],
        ["02 · BUILD", "Собрать рабочий AI-проект", "Studio для ассистента, автоматизации, агента или продукта. Не демо ради демо — проект, который можно объяснить и продолжить.", "/studio", "Открыть Studio →"],
        ["03 · BUSINESS", "Изменить один бизнес-процесс", "Workflow audit, обучение команды или implementation pilot: один процесс, prototype, QA, ownership и handoff.", "/business", "Для бизнеса →"],
      ]
    : [
        ["01 · LEARN", "Learn AI around your real work", "One-to-one for adults, teens and kids: research, writing, code, automation and fact-checking.", "/en/personal", "Choose a learning track →"],
        ["02 · BUILD", "Build a working AI project", "Studio for an assistant, automation, agent or product. Not a demo for its own sake — a project you can explain and keep improving.", "/en/studio", "Open Studio →"],
        ["03 · BUSINESS", "Change one business workflow", "Workflow audit, team training or an implementation pilot: one process, prototype, QA, ownership and handoff.", "/en/business", "For business →"],
      ];

  const prices = ru
    ? [
        ["Start", "$390", "4 занятия", "Базовый AI-процесс и первый полезный результат."],
        ["Personal", "$890", "10 занятий", "Персональная траектория, шаблоны и итоговый проект."],
        ["Intensive", "$1,290", "12 занятий + проект", "Автоматизация, AI-агент, продукт или portfolio."],
        ["Family Concierge", "$1,490", "12 занятий + 2 сессии родителю", "Обучение плюс правила и безопасный контур использования."],
      ]
    : [
        ["Start", "$390", "4 sessions", "A practical AI workflow and first useful result."],
        ["Personal", "$890", "10 sessions", "A tailored learning path, reusable templates and a final project."],
        ["Intensive", "$1,290", "12 sessions + project", "Automation, an AI agent, product or portfolio project."],
        ["Family Concierge", "$1,490", "12 sessions + 2 parent sessions", "Learning plus a practical family safety and usage framework."],
      ];

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <Link href={ru ? "/" : "/en"} className={styles.brand}>
          <span className={styles.mark}>◢◤</span>
          <span>AI Skill Lab</span>
        </Link>
        <nav className={styles.nav} aria-label={ru ? "Основная навигация" : "Main navigation"}>
          <Link href={p("/personal")}>{ru ? "Взрослые" : "Adults"}</Link>
          <Link href={p("/teens")}>{ru ? "Подростки" : "Teens"}</Link>
          <Link href={p("/kids")}>{ru ? "Дети" : "Kids"}</Link>
          <Link href={p("/business")}>{ru ? "Бизнес" : "Business"}</Link>
          <Link href={p("/studio")}>Studio</Link>
          <Link href={p("/pricing")}>{ru ? "Цены" : "Pricing"}</Link>
        </nav>
        <div className={styles.headerActions}>
          <Link href={ru ? "/en" : "/"} className={styles.lang}>{ru ? "EN" : "RU"}</Link>
          <Link href={p("/start")} className={styles.topCta}>{ru ? "Подобрать маршрут" : "Find my route"}</Link>
        </div>
      </header>

      <section className={styles.hero}>
        <div className={styles.heroCopy}>
          <div className={styles.eyebrow}>{ru ? "ПЕРСОНАЛЬНО · ONLINE / PHUKET · RU / EN" : "ONE-TO-ONE · ONLINE / PHUKET · RU / EN"}</div>
          <h1>{ru ? <>Освойте AI так, чтобы <em>результат остался у вас.</em></> : <>Learn AI so the <em>capability stays with you.</em></>}</h1>
          <p>{ru
            ? "Практическое обучение, сборка AI-проектов и внедрение одного бизнес-процесса. Работаем на реальных задачах: вы понимаете решение, проверяете его и можете пользоваться им дальше без магии и зависимости от одного инструмента."
            : "Practical learning, hands-on AI building and one-workflow business implementation. We work on real tasks so you understand the solution, can verify it and can keep using it without depending on one tool or black box."}</p>
          <div className={styles.heroActions}>
            <Link href={p("/start")} className={styles.primary}>{ru ? "Подобрать программу →" : "Find my program →"}</Link>
            <Link href={p("/business")} className={styles.secondary}>{ru ? "Улучшить бизнес-процесс" : "Improve a business workflow"}</Link>
          </div>
          <div className={styles.signals}>
            <span>{ru ? "1-на-1" : "1-to-1"}</span>
            <span>{ru ? "Реальный проект" : "Real project"}</span>
            <span>{ru ? "Human review" : "Human review"}</span>
            <span>{ru ? "Без массового курса" : "Not a mass course"}</span>
          </div>
        </div>
        <aside className={styles.heroPanel}>
          <div className={styles.panelLabel}>{ru ? "ВЫБЕРИТЕ РЕЗУЛЬТАТ" : "CHOOSE THE OUTCOME"}</div>
          <div className={styles.outcome}><strong>LEARN</strong><span>{ru ? "Навык и рабочий процесс" : "Skill + working process"}</span></div>
          <div className={styles.outcome}><strong>BUILD</strong><span>{ru ? "Прототип / ассистент / агент" : "Prototype / assistant / agent"}</span></div>
          <div className={styles.outcome}><strong>BUSINESS</strong><span>{ru ? "Один внедрённый workflow" : "One implemented workflow"}</span></div>
          <div className={styles.panelFoot}>{ru ? "Сначала задача. Потом инструмент." : "Start with the task. Then choose the tool."}</div>
        </aside>
      </section>

      <section className={styles.routeSection}>
        <div className={styles.sectionHead}>
          <span>{ru ? "ТРИ СПОСОБА НАЧАТЬ" : "THREE WAYS TO START"}</span>
          <h2>{ru ? "Не продаём «AI вообще». Выбираем конкретный результат." : "Not “AI in general”. Pick a concrete outcome."}</h2>
        </div>
        <div className={styles.trackGrid}>
          {tracks.map(([tag, title, text, href, cta]) => (
            <article className={styles.track} key={tag}>
              <div className={styles.trackTag}>{tag}</div>
              <h3>{title}</h3>
              <p>{text}</p>
              <Link href={href}>{cta}</Link>
            </article>
          ))}
        </div>
      </section>

      <section className={styles.businessBand}>
        <div>
          <span className={styles.lightEyebrow}>{ru ? "ДЛЯ ОСНОВАТЕЛЕЙ И КОМАНД" : "FOR FOUNDERS AND TEAMS"}</span>
          <h2>{ru ? "Не «добавить AI». Изменить один процесс." : "Don’t “add AI”. Change one workflow."}</h2>
          <p>{ru
            ? "Берём повторяемую работу с понятным владельцем и ценой ошибки. Карта текущего процесса → один ограниченный prototype → QA и human checkpoints → handoff и правила работы."
            : "Take one repeatable workflow with a clear owner and cost of error. Current-state map → one bounded prototype → QA and human checkpoints → handoff and operating rules."}</p>
        </div>
        <div className={styles.businessSteps}>
          <div><b>01</b><span>MAP</span></div>
          <div><b>02</b><span>SELECT</span></div>
          <div><b>03</b><span>TEST</span></div>
          <div><b>04</b><span>HANDOFF</span></div>
        </div>
        <Link href={p("/business")} className={styles.lightCta}>{ru ? "Посмотреть business pilot →" : "See the business pilot →"}</Link>
      </section>

      <section className={styles.pricing}>
        <div className={styles.sectionHead}>
          <span>{ru ? "ПРОЗРАЧНЫЙ СТАРТ" : "CLEAR START"}</span>
          <h2>{ru ? "Для персонального обучения цена понятна заранее." : "Personal learning starts with clear pricing."}</h2>
        </div>
        <div className={styles.priceGrid}>
          {prices.map(([name, price, unit, text]) => (
            <article className={styles.priceCard} key={name}>
              <div className={styles.priceName}>{name}</div>
              <div className={styles.price}>{price}</div>
              <div className={styles.unit}>{unit}</div>
              <p>{text}</p>
            </article>
          ))}
        </div>
        <div className={styles.priceActions}>
          <Link href={p("/pricing")} className={styles.secondary}>{ru ? "Все цены и форматы" : "All pricing and formats"}</Link>
          <Link href={p("/start")} className={styles.primary}>{ru ? "Подобрать программу →" : "Find my program →"}</Link>
        </div>
      </section>

      <section className={styles.proofBand}>
        <div>
          <span>{ru ? "ПРОВЕРЯЕМЫЙ ПОДХОД" : "VERIFIABLE PRACTICE"}</span>
          <h2>{ru ? "Proof остаётся — но после оффера, а не вместо него." : "Proof stays — after the offer, not instead of it."}</h2>
        </div>
        <p>{ru
          ? "На проектах фиксируем источники, тесты, human checkpoints, privacy boundaries и fallback. Технические release-гейты доступны отдельно тем, кому они действительно нужны."
          : "Projects make sources, tests, human checkpoints, privacy boundaries and fallback explicit. Release-engineering evidence remains available separately for people who actually need it."}</p>
        <Link href={p("/proof")} className={styles.proofLink}>{ru ? "Открыть Proof Lab →" : "Open Proof Lab →"}</Link>
      </section>

      <section className={styles.finalCta}>
        <span>{ru ? "ПЕРВЫЙ ШАГ" : "FIRST STEP"}</span>
        <h2>{ru ? "Опишите задачу, уровень и желаемый результат." : "Describe the task, your level and the result you want."}</h2>
        <p>{ru ? "Мы начнём с задачи и подберём минимальный маршрут, который даёт проверяемый результат." : "We’ll start from the task and choose the smallest route that produces a verifiable result."}</p>
        <Link href={p("/start")} className={styles.primary}>{ru ? "Начать →" : "Start →"}</Link>
      </section>

      <footer className={styles.footer}>
        <strong>AI Skill Lab</strong>
        <span>© 2026 · Phuket / online</span>
        <nav>
          <Link href={p("/business")}>{ru ? "Бизнес" : "Business"}</Link>
          <Link href={p("/studio")}>Studio</Link>
          <Link href={p("/pricing")}>{ru ? "Цены" : "Pricing"}</Link>
          <Link href={p("/method")}>{ru ? "Метод" : "Method"}</Link>
          <Link href={p("/proof")}>Proof</Link>
        </nav>
      </footer>
    </main>
  );
}
