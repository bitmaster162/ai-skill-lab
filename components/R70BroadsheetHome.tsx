"use client";

import React, { useState } from "react";
import Link from "next/link";
import styles from "./R70BroadsheetHome.module.css";

export type Locale = "ru" | "en";

interface BroadsheetHomeProps {
  locale?: Locale;
}

export function R70BroadsheetHome({ locale = "ru" }: BroadsheetHomeProps) {
  const isRu = locale === "ru";
  const [audience, setAudience] = useState<"all" | "kids" | "teens" | "adults" | "business">("all");
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  // Audience matching logic
  const isMatched = (progIndex: string): boolean => {
    if (audience === "all") return false;
    if (progIndex === "p01") return audience === "adults";
    if (progIndex === "p02") return audience === "adults" || audience === "teens";
    if (progIndex === "p03") return audience === "business";
    if (progIndex === "p04") return audience === "kids";
    if (progIndex === "p05") return audience === "teens";
    return false;
  };

  return (
    <div className={styles.pageRoot} data-paper="1">
      {/* ----------------------------------------------------
          HEADER & ACCESSIBLE NAVIGATION
          ---------------------------------------------------- */}
      <header className={styles.header}>
        <Link href={isRu ? "/" : "/en"} className={styles.wordmark} aria-label="AI Skill Lab — Home">
          <span className={styles.wordmarkGlyph} aria-hidden="true">◢◤</span>
          <span>AI Skill Lab</span>
        </Link>

        <nav className={styles.navLinks} aria-label={isRu ? "Основная навигация" : "Main navigation"}>
          <Link href={isRu ? "/kids" : "/en/kids"} className={styles.navLink}>{isRu ? "Дети" : "Kids"}</Link>
          <Link href={isRu ? "/teens" : "/en/teens"} className={styles.navLink}>{isRu ? "Подростки" : "Teens"}</Link>
          <Link href={isRu ? "/personal" : "/en/personal"} className={styles.navLink}>{isRu ? "Взрослые" : "Adults"}</Link>
          <Link href={isRu ? "/business" : "/en/business"} className={styles.navLink}>{isRu ? "Бизнес" : "Business"}</Link>
          <span className={styles.navDivider} aria-hidden="true" />
          <Link href={isRu ? "/studio" : "/en/studio"} className={`${styles.navLink} ${styles.navLinkTeal}`}>Studio</Link>
          <Link href={isRu ? "/pricing" : "/en/pricing"} className={styles.navLink}>{isRu ? "Цены" : "Pricing"}</Link>
          <Link href={isRu ? "/method" : "/en/method"} className={styles.navLink}>{isRu ? "Метод" : "Method"}</Link>
          <Link href={isRu ? "/proof" : "/en/proof"} className={styles.navLink}>Proof</Link>
        </nav>

        <div className={styles.headerActions}>
          <div className={styles.langGroup} role="group" aria-label={isRu ? "Выбор языка" : "Language selector"}>
            <Link
              href="/"
              className={`${styles.langBtn} ${isRu ? styles.langBtnActive : ""}`}
              aria-current={isRu ? "page" : undefined}
            >
              RU
            </Link>
            <Link
              href="/en"
              className={`${styles.langBtn} ${!isRu ? styles.langBtnActive : ""}`}
              aria-current={!isRu ? "page" : undefined}
            >
              EN
            </Link>
          </div>

          <Link href={isRu ? "/proof" : "/en/proof"} className={styles.headerCta}>
            {isRu ? "Запустить Proof Lab" : "Launch Proof Lab"}
          </Link>

          <button
            type="button"
            className={styles.menuToggle}
            aria-label={isRu ? "Открыть меню" : "Open menu"}
            aria-expanded={isMenuOpen}
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? "✕" : "≡"}
          </button>
        </div>
      </header>

      {/* Mobile Menu Dropdown */}
      {isMenuOpen && (
        <nav className={styles.mobileMenuDropdown} aria-label={isRu ? "Мобильная навигация" : "Mobile navigation"}>
          <Link href={isRu ? "/kids" : "/en/kids"} onClick={() => setIsMenuOpen(false)}>{isRu ? "Дети 8–13" : "Kids 8–13"}</Link>
          <Link href={isRu ? "/teens" : "/en/teens"} onClick={() => setIsMenuOpen(false)}>{isRu ? "Подростки 14–18" : "Teens 14–18"}</Link>
          <Link href={isRu ? "/personal" : "/en/personal"} onClick={() => setIsMenuOpen(false)}>{isRu ? "Взрослым" : "Adults"}</Link>
          <Link href={isRu ? "/business" : "/en/business"} onClick={() => setIsMenuOpen(false)}>{isRu ? "Бизнес" : "Business"}</Link>
          <Link href={isRu ? "/studio" : "/en/studio"} onClick={() => setIsMenuOpen(false)}>Studio</Link>
          <Link href={isRu ? "/pricing" : "/en/pricing"} onClick={() => setIsMenuOpen(false)}>{isRu ? "Цены" : "Pricing"}</Link>
          <Link href={isRu ? "/method" : "/en/method"} onClick={() => setIsMenuOpen(false)}>{isRu ? "Метод" : "Method"}</Link>
          <Link href={isRu ? "/proof" : "/en/proof"} onClick={() => setIsMenuOpen(false)}>Proof Lab</Link>
          <Link href={isRu ? "/start" : "/en/start"} onClick={() => setIsMenuOpen(false)}>{isRu ? "Подобрать программу →" : "Find my program →"}</Link>
        </nav>
      )}

      <main id="main">
        {/* ----------------------------------------------------
            MASTHEAD (HERO)
            ---------------------------------------------------- */}
        <section className={styles.masthead} id="top" aria-label={isRu ? "Заглавная страница" : "Masthead"}>
          <aside className={styles.mastheadMarginalia} aria-label={isRu ? "Формат и гейты" : "Format and gates"}>
            <p className={styles.marginaliaLocation}>
              {isRu ? <>Персональное обучение AI<br />online / Phuket</> : <>Personal AI education<br />online / Phuket</>}
            </p>
            <ul className={styles.marginaliaGates}>
              <li><span className={styles.gateMarker} aria-hidden="true">▸</span>0 PUBLIC FORMS</li>
              <li><span className={styles.gateMarker} aria-hidden="true">▸</span>HASHED CSP</li>
              <li><span className={styles.gateMarker} aria-hidden="true">▸</span>HUMAN-GATED</li>
              <li><span className={styles.gateMarker} aria-hidden="true">▸</span>BYTE-EXACT</li>
            </ul>
            <p className={styles.marginaliaMeta}>
              Evidence class: <span className={styles.badgeGate}>GATE</span> — {isRu ? "автоматический гейт проекта" : "automated project gate"}
            </p>
          </aside>

          <div className={styles.mastheadMain}>
            <h1>
              {isRu ? (
                <>AI не должен<br />делать вас <em>зависимее.</em></>
              ) : (
                <>AI should not make you<br /><em>more dependent.</em></>
              )}
            </h1>
            <p className={styles.leadText}>
              {isRu
                ? "Он должен делать вас сильнее. Учимся исследовать, создавать, автоматизировать и собирать собственные AI-процессы на реальных задачах."
                : "It should make you more capable. Learn to research, create, automate and build reliable AI workflows around real tasks."}
            </p>
            <div className={styles.mastheadActions}>
              <Link href={isRu ? "/proof" : "/en/proof"} className={styles.btnPrimaryLarge}>
                {isRu ? "Запустить Proof Lab →" : "Launch Proof Lab →"}
              </Link>
              <Link href={isRu ? "/start" : "/en/start"} className={styles.btnGhostLarge}>
                {isRu ? "Подобрать программу" : "Find my program"}
              </Link>
            </div>
          </div>

          <div className={styles.architectureCard}>
            <h2>{isRu ? "Архитектура процессов" : "Process Architecture"}</h2>
            <ul className={styles.archList}>
              <li className={styles.archItem}>
                <div className={styles.archItemTop}>
                  <span className={`${styles.archTag} ${styles.archTagLearn}`}>01 · LEARN</span>
                  <span className={styles.archStatus}>LIVE / 1-ON-1</span>
                </div>
                <p className={styles.archText}>
                  {isRu
                    ? "Практические навыки: постановка задачи, фактчекинг и личные workflow."
                    : "Practical skills: task specification, fact-checking and personal workflows."}
                </p>
              </li>
              <li className={styles.archItem}>
                <div className={styles.archItemTop}>
                  <span className={`${styles.archTag} ${styles.archTagBuild}`}>02 · BUILD</span>
                  <span className={styles.archStatus}>STUDIO / BRIDGE</span>
                </div>
                <p className={styles.archText}>
                  {isRu
                    ? "Сборка прототипов, ассистентов, агентов и системных решений."
                    : "Building prototypes, assistants, agents and governed systems."}
                </p>
              </li>
              <li className={styles.archItem}>
                <div className={styles.archItemTop}>
                  <span className={`${styles.archTag} ${styles.archTagOperate}`}>03 · OPERATE</span>
                  <span className={styles.archStatus}>ROADMAP / FUTURE</span>
                </div>
                <p className={styles.archText}>
                  {isRu
                    ? "Управление агентами и процессами. Планируется в следующих релизах."
                    : "Agent ops and governance. Planned in future releases."}
                </p>
              </li>
            </ul>
          </div>
        </section>

        {/* ----------------------------------------------------
            TRUST STRIP
            ---------------------------------------------------- */}
        <section className={styles.trustStrip} aria-label={isRu ? "Принципы обучения" : "Guiding principles"}>
          <div className={styles.trustCell}>
            <span className={styles.trustIndex}>01 · {isRu ? "ФОРМАТ" : "FORMAT"}</span>
            <h3 className={styles.trustTitle}>{isRu ? "Не массовый курс" : "Not a mass course"}</h3>
            <p className={styles.trustDesc}>
              {isRu ? "Маршрут собирается под задачу конкретного человека или команды." : "Route is built around the specific goal of the learner or team."}
            </p>
          </div>
          <div className={styles.trustCell}>
            <span className={styles.trustIndex}>02 · {isRu ? "ПРАКТИКА" : "PRACTICE"}</span>
            <h3 className={styles.trustTitle}>{isRu ? "Работа руками" : "Hands-on building"}</h3>
            <p className={styles.trustDesc}>
              {isRu ? "Большая часть времени уходит на сборку, проверку и решение задач." : "Most time is spent building, verifying and solving actual tasks."}
            </p>
          </div>
          <div className={styles.trustCell}>
            <span className={styles.trustIndex}>03 · {isRu ? "ИТОГ" : "OUTCOME"}</span>
            <h3 className={styles.trustTitle}>{isRu ? "Проверяемый результат" : "Visible output"}</h3>
            <p className={styles.trustDesc}>
              {isRu ? "На выходе остаётся артефакт, готовый процесс или portfolio project." : "A finished artifact, workflow or portfolio project remains at the end."}
            </p>
          </div>
          <div className={styles.trustCell}>
            <span className={styles.trustIndex}>04 · {isRu ? "ЭТИКА" : "ETHICS"}</span>
            <h3 className={styles.trustTitle}>Responsible AI</h3>
            <p className={styles.trustDesc}>
              {isRu ? "Фактчекинг, приватность данных, границы применимости и контроль." : "Fact-checking, data privacy, failure modes and human ownership."}
            </p>
          </div>
        </section>

        {/* ----------------------------------------------------
            DARK PROOF SECTION (ISLAND)
            ---------------------------------------------------- */}
        <section className={styles.proofSection} id="proof" aria-label={isRu ? "Доказательства и гейты" : "Proof and gates"}>
          <div className={styles.proofGrid}>
            <div className={styles.proofLeft}>
              <span className={styles.proofKicker}>01 / Site as proof</span>
              <h2>
                {isRu ? (
                  <>Этот сайт не говорит,<br /><em>что мы умеем AI.</em><br />Он это показывает.</>
                ) : (
                  <>This site does not tell you<br /><em>we can build with AI.</em><br />It shows you.</>
                )}
              </h2>
              <p className={styles.proofDesc}>
                {isRu
                  ? "Source/static parity, privacy без trackers, hashed CSP, runtime smoke, release manifest и byte-exact reconstruction. Это реальные гейты проекта, а не декоративные бейджи."
                  : "Source/static parity, tracker-free privacy, hashed CSP, runtime smoke tests, release manifest and byte-exact reconstruction. Real project gates, not decorative badges."}
              </p>

              <div className={styles.proofClassLegend}>
                <p className={styles.proofClassTitle}>{isRu ? "Классы доказательств" : "Evidence Classes"}</p>
                <div className={styles.proofClassRows}>
                  <div><strong className={styles.badgeGateDark}>GATE:</strong> {isRu ? "Автоматический release-тест, проверяемый машиной." : "Automated machine-verified release test."}</div>
                  <div><strong className={styles.badgeArtifactDark}>ARTIFACT:</strong> {isRu ? "Исходный код, manifest или проверяемый лог." : "Source code, manifest or verifiable log."}</div>
                  <div><strong className={styles.badgeStatedDark}>STATED:</strong> {isRu ? "Заявление основателя или экспертная позиция." : "Founder statement or expert position."}</div>
                </div>
              </div>
            </div>

            <div className={styles.proofRight}>
              <div className={styles.proofBoard} aria-label={isRu ? "Гейты релизной системы" : "Release system gates"}>
                <div className={styles.proofBoardHeader}>
                  <span className={styles.proofBoardTitle}>AI SKILL LAB / R74 LIVE VERIFIED EVIDENCE</span>
                  <span className={styles.proofBoardBadge}>● R74 LIVE VERIFIED</span>
                </div>
                <ul className={styles.proofGateList}>
                  <li className={styles.proofGateRow}>
                    <span className={styles.proofGateName}>01 · broken_links</span>
                    <span className={styles.proofGateVal}>0 / PASS</span>
                    <span className={styles.proofGateClass}>GATE</span>
                  </li>
                  <li className={styles.proofGateRow}>
                    <span className={styles.proofGateName}>02 · public_forms + trackers</span>
                    <span className={styles.proofGateVal}>0 / PASS</span>
                    <span className={styles.proofGateClass}>GATE</span>
                  </li>
                  <li className={styles.proofGateRow}>
                    <span className={styles.proofGateName}>03 · client_runtime_smoke</span>
                    <span className={styles.proofGateVal}>SMOKE TESTED</span>
                    <span className={styles.proofGateClass}>GATE</span>
                  </li>
                  <li className={styles.proofGateRow}>
                    <span className={styles.proofGateName}>04 · script_policy</span>
                    <span className={styles.proofGateVal}>HASHED CSP</span>
                    <span className={styles.proofGateClass}>GATE</span>
                  </li>
                  <li className={styles.proofGateRow}>
                    <span className={styles.proofGateName}>05 · release_payload</span>
                    <span className={styles.proofGateVal}>SHA-256</span>
                    <span className={styles.proofGateClass}>ARTIFACT</span>
                  </li>
                  <li className={styles.proofGateRow}>
                    <span className={styles.proofGateName}>06 · reconstruction</span>
                    <span className={styles.proofGateVal}>BYTE-EXACT</span>
                    <span className={styles.proofGateClass}>ARTIFACT</span>
                  </li>
                </ul>
              </div>

              <div className={styles.defectCard}>
                <span className={styles.defectTitle}>{isRu ? "Честное раскрытие дефектов" : "Defect Disclosure"}</span>
                <p className={styles.defectText}>
                  {isRu
                    ? "R74 LIVE VERIFIED. R74 был promoted одной SHA-bound попыткой из exact qualified preview. Vercel создал новый production deployment, а platform metadata связывает его с exact qualified preview; production затем независимо проверен по exact R74 manifest и required 6/6 live route smoke."
                    : "R74 LIVE VERIFIED. R74 was promoted in one SHA-bound attempt from the exact qualified preview. Vercel created a new production deployment, and platform metadata binds it to that exact qualified preview; production was then independently verified against the exact R74 manifest and the required 6/6 live route smoke."}
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ----------------------------------------------------
            AUDIENCE ROUTER & PROGRAM INDEX
            ---------------------------------------------------- */}
        <section className={styles.sectionWhite} id="programs">
          <div className={styles.sectionHeader}>
            <span className={styles.sectionKicker}>02 / CHOOSE A TRACK</span>
            <h2>{isRu ? "Один AI. Совсем разные задачи." : "One technology. Very different outcomes."}</h2>
          </div>

          <div className={styles.audienceFilterGroup} role="group" aria-label={isRu ? "Фильтр по аудитории" : "Filter by audience"}>
            <button
              type="button"
              className={`${styles.filterBtn} ${audience === "all" ? styles.filterBtnActive : ""}`}
              onClick={() => setAudience("all")}
            >
              {isRu ? "Все направления" : "All tracks"}
            </button>
            <button
              type="button"
              className={`${styles.filterBtn} ${audience === "adults" ? styles.filterBtnActive : ""}`}
              onClick={() => setAudience("adults")}
            >
              {isRu ? "Взрослые" : "Adults"}
            </button>
            <button
              type="button"
              className={`${styles.filterBtn} ${audience === "kids" ? styles.filterBtnActive : ""}`}
              onClick={() => setAudience("kids")}
            >
              {isRu ? "Дети 8–13" : "Kids 8–13"}
            </button>
            <button
              type="button"
              className={`${styles.filterBtn} ${audience === "teens" ? styles.filterBtnActive : ""}`}
              onClick={() => setAudience("teens")}
            >
              {isRu ? "Подростки 14–18" : "Teens 14–18"}
            </button>
            <button
              type="button"
              className={`${styles.filterBtn} ${audience === "business" ? styles.filterBtnActive : ""}`}
              onClick={() => setAudience("business")}
            >
              {isRu ? "Команда / Бизнес" : "Teams & Business"}
            </button>
          </div>

          <div className={styles.programIndex}>
            {/* 01 */}
            <Link
              href={isRu ? "/start" : "/en/start"}
              id="p01"
              className={`${styles.programRow} ${isMatched("p01") ? styles.programRowMatched : ""}`}
            >
              <span className={styles.programNum}>01</span>
              <div className={styles.programTitleGroup}>
                <h3 className={styles.programTitle}>{isRu ? "AI для жизни и работы" : "AI for work & life"}</h3>
                <p className={styles.programDesc}>
                  {isRu
                    ? "ChatGPT, Gemini, Claude и другие модели как рабочая система: исследования, тексты, анализ, решения и личные процессы."
                    : "Use modern models for research, writing, analysis, decisions and repeatable personal workflows."}
                </p>
              </div>
              <div className={styles.programMetaGroup}>
                <span className={styles.programMeta}>{isRu ? "1-на-1 · с нуля" : "1:1 · beginner-friendly"}</span>
                <span className={styles.programMeta}>{isRu ? "Взрослые" : "Adults"}</span>
              </div>
              <div className={styles.programSlot}>
                {isMatched("p01") && <span className={styles.matchBadge}>MATCH</span>}
              </div>
            </Link>

            {/* 02 */}
            <Link
              href={isRu ? "/start" : "/en/start"}
              id="p02"
              className={`${styles.programRow} ${isMatched("p02") ? styles.programRowMatched : ""}`}
            >
              <span className={styles.programNum}>02</span>
              <div className={styles.programTitleGroup}>
                <h3 className={styles.programTitle}>AI Builder</h3>
                <p className={styles.programDesc}>
                  {isRu
                    ? "Ассистенты, автоматизации, агенты и простые AI-продукты. Меньше лекций — больше сборки руками."
                    : "Build assistants, automations, agents and lightweight AI products instead of only learning prompts."}
                </p>
              </div>
              <div className={styles.programMetaGroup}>
                <span className={styles.programMeta}>{isRu ? "Практика · проекты" : "projects · systems"}</span>
                <span className={styles.programMeta}>{isRu ? "Взрослые / Подростки" : "Adults / Teens"}</span>
              </div>
              <div className={styles.programSlot}>
                {isMatched("p02") && <span className={styles.matchBadge}>MATCH</span>}
              </div>
            </Link>

            {/* 03 */}
            <Link
              href={isRu ? "/business" : "/en/business"}
              id="p03"
              className={`${styles.programRow} ${isMatched("p03") ? styles.programRowMatched : ""}`}
            >
              <span className={styles.programNum}>03</span>
              <div className={styles.programTitleGroup}>
                <h3 className={styles.programTitle}>{isRu ? "AI для бизнеса" : "AI for business"}</h3>
                <p className={styles.programDesc}>
                  {isRu
                    ? "Разбираем процессы команды, выбираем точки внедрения и обучаем сотрудников использовать AI измеримо и безопасно."
                    : "Map team workflows, identify useful AI insertion points and train people around measurable tasks."}
                </p>
              </div>
              <div className={styles.programMetaGroup}>
                <span className={styles.programMeta}>{isRu ? "Команды · процессы" : "teams · processes"}</span>
                <span className={styles.programMeta}>{isRu ? "Бизнес" : "Business"}</span>
              </div>
              <div className={styles.programSlot}>
                {isMatched("p03") && <span className={styles.matchBadge}>MATCH</span>}
              </div>
            </Link>

            {/* 04 */}
            <Link
              href={isRu ? "/kids" : "/en/kids"}
              id="p04"
              className={`${styles.programRow} ${isMatched("p04") ? styles.programRowMatched : ""}`}
            >
              <span className={styles.programNum}>04</span>
              <div className={styles.programTitleGroup}>
                <h3 className={styles.programTitle}>{isRu ? "AI для детей" : "AI for kids"}</h3>
                <p className={styles.programDesc}>
                  {isRu
                    ? "8–13 лет: творчество, исследования, критическое мышление и собственный проект без модели «сделай за меня»."
                    : "Ages 8–13: creativity, research, critical thinking, privacy and a project they can explain themselves."}
                </p>
              </div>
              <div className={styles.programMetaGroup}>
                <span className={styles.programMeta}>8–13 · {isRu ? "родительский контакт" : "adult contact"}</span>
                <span className={styles.programMeta}>{isRu ? "Дети" : "Kids"}</span>
              </div>
              <div className={styles.programSlot}>
                {isMatched("p04") && <span className={styles.matchBadge}>MATCH</span>}
              </div>
            </Link>

            {/* 05 */}
            <Link
              href={isRu ? "/teens" : "/en/teens"}
              id="p05"
              className={`${styles.programRow} ${isMatched("p05") ? styles.programRowMatched : ""}`}
            >
              <span className={styles.programNum}>05</span>
              <div className={styles.programTitleGroup}>
                <h3 className={styles.programTitle}>{isRu ? "AI для подростков" : "AI for teens"}</h3>
                <p className={styles.programDesc}>
                  {isRu
                    ? "14–18 лет: AI как реальный навык для учёбы, портфолио, первых проектов, кода и будущей профессии."
                    : "Ages 14–18: research, code, automation, portfolio work and the beginnings of real AI product thinking."}
                </p>
              </div>
              <div className={styles.programMetaGroup}>
                <span className={styles.programMeta}>14–18 · portfolio</span>
                <span className={styles.programMeta}>{isRu ? "Подростки" : "Teens"}</span>
              </div>
              <div className={styles.programSlot}>
                {isMatched("p05") && <span className={styles.matchBadge}>MATCH</span>}
              </div>
            </Link>
          </div>
        </section>

        {/* ----------------------------------------------------
            CAPABILITY MATRIX
            ---------------------------------------------------- */}
        <section className={styles.sectionWhite} aria-label={isRu ? "Матрица возможностей AI" : "AI Capability Matrix"}>
          <div className={styles.sectionHeader}>
            <span className={styles.sectionKicker}>03 / AI Capability Matrix</span>
            <h2>{isRu ? "Не набор промптов. Система от входа до результата." : "Not a bag of prompts. A system from input to shipped output."}</h2>
          </div>

          <div className={styles.matrixGrid}>
            <article className={styles.matrixCard}>
              <div className={styles.matrixHeader}>
                <span className={styles.matrixIndex}>01</span>
                <h3 className={styles.matrixTitle}>RESEARCH</h3>
              </div>
              <dl className={styles.matrixDl}>
                <div className={styles.matrixRow}>
                  <dt className={styles.matrixDt}>INPUT</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Размытый вопрос, много источников, противоречия." : "A fuzzy question, many sources and conflicting claims."}
                  </dd>
                </div>
                <div className={styles.matrixRow}>
                  <dt className={styles.matrixDt}>AI LAYER</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Поиск вариантов, сравнение evidence, synthesis и карта неопределённости." : "Search expansion, evidence comparison, synthesis and uncertainty mapping."}
                  </dd>
                </div>
                <div className={`${styles.matrixRow} ${styles.matrixHumanGate}`}>
                  <dt className={styles.matrixDt}>HUMAN GATE</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Качество источников, спорные места, допущения и финальное решение." : "Source quality, disputed points, assumptions and final judgement."}
                  </dd>
                </div>
                <div className={styles.matrixRow}>
                  <dt className={styles.matrixDt}>SHIP</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Source-backed brief + source map + next action." : "Source-backed brief + source map + next action."}
                  </dd>
                </div>
              </dl>
            </article>

            <article className={styles.matrixCard}>
              <div className={styles.matrixHeader}>
                <span className={styles.matrixIndex}>02</span>
                <h3 className={styles.matrixTitle}>BUILD</h3>
              </div>
              <dl className={styles.matrixDl}>
                <div className={styles.matrixRow}>
                  <dt className={styles.matrixDt}>INPUT</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Идея продукта, ассистента или внутреннего инструмента." : "A product, assistant or internal-tool idea."}
                  </dd>
                </div>
                <div className={styles.matrixRow}>
                  <dt className={styles.matrixDt}>AI LAYER</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Спецификация, варианты UI/code, прототипирование и test scaffolding." : "Specification, UI/code options, prototyping and test scaffolding."}
                  </dd>
                </div>
                <div className={`${styles.matrixRow} ${styles.matrixHumanGate}`}>
                  <dt className={styles.matrixDt}>HUMAN GATE</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Scope, продуктовые решения, QA, ограничения и release gate." : "Scope, product decisions, QA, limitations and release gate."}
                  </dd>
                </div>
                <div className={styles.matrixRow}>
                  <dt className={styles.matrixDt}>SHIP</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Working prototype + tests + known limits + handoff." : "Working prototype + tests + known limits + handoff."}
                  </dd>
                </div>
              </dl>
            </article>

            <article className={styles.matrixCard}>
              <div className={styles.matrixHeader}>
                <span className={styles.matrixIndex}>03</span>
                <h3 className={styles.matrixTitle}>AUTOMATE</h3>
              </div>
              <dl className={styles.matrixDl}>
                <div className={styles.matrixRow}>
                  <dt className={styles.matrixDt}>INPUT</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Повторяемый процесс, который отнимает время и внимание." : "A repeatable process consuming time and attention."}
                  </dd>
                </div>
                <div className={styles.matrixRow}>
                  <dt className={styles.matrixDt}>AI LAYER</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Декомпозиция, routing, transformations, шаблоны и glue-code." : "Decomposition, routing, transformations, templates and glue code."}
                  </dd>
                </div>
                <div className={`${styles.matrixRow} ${styles.matrixHumanGate}`}>
                  <dt className={styles.matrixDt}>HUMAN GATE</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Permissions, failure modes, rollback, owner и acceptance criteria." : "Permissions, failure modes, rollback, owner and acceptance criteria."}
                  </dd>
                </div>
                <div className={styles.matrixRow}>
                  <dt className={styles.matrixDt}>SHIP</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Workflow / agent + fallback + operating instructions." : "Workflow / agent + fallback + operating instructions."}
                  </dd>
                </div>
              </dl>
            </article>

            <article className={styles.matrixCard}>
              <div className={styles.matrixHeader}>
                <span className={styles.matrixIndex}>04</span>
                <h3 className={styles.matrixTitle}>TEACH</h3>
              </div>
              <dl className={styles.matrixDl}>
                <div className={styles.matrixRow}>
                  <dt className={styles.matrixDt}>INPUT</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Навык, который человек хочет уметь применять самостоятельно." : "A skill a person wants to apply independently."}
                  </dd>
                </div>
                <div className={styles.matrixRow}>
                  <dt className={styles.matrixDt}>AI LAYER</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Объяснение, упражнения, варианты, критика черновиков и практика." : "Explanation, exercises, alternatives, draft critique and practice."}
                  </dd>
                </div>
                <div className={`${styles.matrixRow} ${styles.matrixHumanGate}`}>
                  <dt className={styles.matrixDt}>HUMAN GATE</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Понимание, авторство, фактчекинг и способность защитить решение." : "Understanding, authorship, fact-checking and ability to defend the work."}
                  </dd>
                </div>
                <div className={styles.matrixRow}>
                  <dt className={styles.matrixDt}>SHIP</dt>
                  <dd className={styles.matrixDd}>
                    {isRu ? "Project + explanation + repeatable process + checklist." : "Project + explanation + repeatable process + checklist."}
                  </dd>
                </div>
              </dl>
            </article>
          </div>

          {/* Youth bridge cards */}
          <div className={styles.youthBridgeGrid}>
            <Link href={isRu ? "/kids" : "/en/kids"} className={styles.youthCardLink}>
              <span className={styles.youthAgeBand}>{isRu ? "8–13 лет" : "Ages 8–13"}</span>
              <h3 className={styles.youthCardTitle}>{isRu ? "Дети: творчество и безопасные привычки" : "Kids: creativity and safe habits"}</h3>
              <p className={styles.youthCardDesc}>
                {isRu
                  ? "Разбираемся, как устроен AI, создаём первые проекты и учимся критически проверять ответы без зависимости."
                  : "Understand how AI works, build first creative projects, and learn to critically verify answers."}
              </p>
            </Link>
            <Link href={isRu ? "/teens" : "/en/teens"} className={styles.youthCardLink}>
              <span className={styles.youthAgeBand}>{isRu ? "14–18 лет" : "Ages 14–18"}</span>
              <h3 className={styles.youthCardTitle}>{isRu ? "Подростки: код, портфолио и продукты" : "Teens: code, portfolio and products"}</h3>
              <p className={styles.youthCardDesc}>
                {isRu
                  ? "Реальный навык для учёбы и будущей профессии: от автоматизаций и ассистентов до самостоятельных приложений."
                  : "A real capability for study and future careers: from automations and assistants to standalone applications."}
              </p>
            </Link>
          </div>
        </section>

        {/* ----------------------------------------------------
            METHOD RAIL
            ---------------------------------------------------- */}
        <section className={styles.sectionWhite} id="method">
          <div className={styles.sectionHeader}>
            <span className={styles.sectionKicker}>{isRu ? "Метод" : "Method"}</span>
            <h2>{isRu ? "Цель → практика → система → проект" : "Goal → practice → system → project"}</h2>
          </div>

          <div className={styles.methodGrid}>
            <div className={styles.methodStep}>
              <span className={styles.methodStepNum}>01</span>
              <h3 className={styles.methodStepTitle}>{isRu ? "Диагностика" : "Diagnosis"}</h3>
              <p className={styles.methodStepText}>
                {isRu ? "Фиксируем уровень, интересы, ограничения и конкретный результат." : "Define current level, interests, constraints and a concrete outcome."}
              </p>
            </div>
            <div className={styles.methodStep}>
              <span className={styles.methodStepNum}>02</span>
              <h3 className={styles.methodStepTitle}>{isRu ? "Персональный маршрут" : "Personal route"}</h3>
              <p className={styles.methodStepText}>
                {isRu ? "Убираем лишние модули и выбираем только нужные инструменты." : "Remove irrelevant modules and choose only useful tools."}
              </p>
            </div>
            <div className={styles.methodStep}>
              <span className={styles.methodStepNum}>03</span>
              <h3 className={styles.methodStepTitle}>{isRu ? "Сборка руками" : "Build by doing"}</h3>
              <p className={styles.methodStepText}>
                {isRu ? "Каждое занятие даёт артефакт: шаблон, исследование, workflow или часть проекта." : "Every session produces an artifact or a piece of the final project."}
              </p>
            </div>
            <div className={styles.methodStep}>
              <span className={styles.methodStepNum}>04</span>
              <h3 className={styles.methodStepTitle}>{isRu ? "Финальный проект" : "Final project"}</h3>
              <p className={styles.methodStepText}>
                {isRu ? "Ученик объясняет логику работы, ограничения AI и собственный вклад." : "The learner explains the logic, limitations and their own contribution."}
              </p>
            </div>
          </div>
        </section>

        {/* ----------------------------------------------------
            PRICING GRID
            ---------------------------------------------------- */}
        <section className={styles.sectionWhite} id="pricing">
          <div className={styles.sectionHeader}>
            <span className={styles.sectionKicker}>04 / ENGAGE</span>
            <h2>{isRu ? "Можно проверить формат до большого пакета" : "Start small if you want to test the format first"}</h2>
          </div>

          <div className={styles.pricingGrid}>
            {/* Start */}
            <article className={styles.pricingCard}>
              <span className={styles.pricingPlan}>Start</span>
              <div className={styles.pricingPrice}>$390</div>
              <span className={styles.pricingLength}>{isRu ? "4 занятия" : "4 sessions"}</span>
              <p className={styles.pricingDesc}>
                {isRu
                  ? "Разобраться в AI, настроить базовый рабочий процесс и получить первый полезный результат."
                  : "Build a useful baseline workflow and understand what to learn next."}
              </p>
              <Link href={isRu ? "/start" : "/en/start"} className={`${styles.pricingBtn} ${styles.pricingBtnGhost}`}>
                {isRu ? "Выбрать Start" : "Choose Start"}
              </Link>
            </article>

            {/* Personal */}
            <article className={`${styles.pricingCard} ${styles.pricingCardFeatured}`}>
              <span className={styles.popularBadge}>{isRu ? "Основной" : "Core"}</span>
              <span className={styles.pricingPlan}>Personal</span>
              <div className={styles.pricingPrice}>$890</div>
              <span className={styles.pricingLength}>{isRu ? "10 занятий" : "10 sessions"}</span>
              <p className={styles.pricingDesc}>
                {isRu
                  ? "Полная персональная траектория: практика, материалы, собственные шаблоны и итоговый проект."
                  : "Full personal route with practice, reusable templates and a final project."}
              </p>
              <Link href={isRu ? "/start" : "/en/start"} className={`${styles.pricingBtn} ${styles.pricingBtnPrimary}`}>
                {isRu ? "Выбрать Personal" : "Choose Personal"}
              </Link>
            </article>

            {/* Intensive */}
            <article className={styles.pricingCard}>
              <span className={styles.pricingPlan}>Intensive</span>
              <div className={styles.pricingPrice}>$1,290</div>
              <span className={styles.pricingLength}>{isRu ? "12 занятий + проект" : "12 sessions + project"}</span>
              <p className={styles.pricingDesc}>
                {isRu
                  ? "Для сложной задачи: автоматизация, AI-агент, мини-продукт или технический portfolio project."
                  : "For a more technical automation, agent, mini-product or portfolio project."}
              </p>
              <Link href={isRu ? "/start" : "/en/start"} className={`${styles.pricingBtn} ${styles.pricingBtnGhost}`}>
                {isRu ? "Выбрать Intensive" : "Choose Intensive"}
              </Link>
            </article>

            {/* Family Concierge */}
            <article className={`${styles.pricingCard} ${styles.pricingCardDark}`}>
              <span className={styles.pricingPlan}>Family Concierge</span>
              <div className={styles.pricingPrice}>$1,490</div>
              <span className={styles.pricingLength}>{isRu ? "12 занятий + 2 сессии родителю" : "12 learner sessions + 2 parent sessions"}</span>
              <p className={styles.pricingDesc}>
                {isRu
                  ? "Индивидуальный трек ребёнка, отдельные встречи со взрослым, семейные правила AI и защита проекта."
                  : "Personal learner track, separate parent sessions, home AI safety setup and final presentation."}
              </p>
              <Link href={isRu ? "/start" : "/en/start"} className={`${styles.pricingBtn} ${styles.pricingBtnDark}`}>
                {isRu ? "Обсудить Family" : "Discuss Family"}
              </Link>
            </article>
          </div>
        </section>

        {/* ----------------------------------------------------
            ENTRY TOOLS & FORMULA
            ---------------------------------------------------- */}
        <section className={styles.sectionWhite} id="start">
          <div className={styles.sectionHeader}>
            <span className={styles.sectionKicker}>{isRu ? "Инструменты" : "Interactive Tools"}</span>
            <h2>{isRu ? "Инструменты подбора и расчета" : "Entry & Sensitivity Tools"}</h2>
          </div>

          <div className={styles.toolsGrid}>
            <Link href={isRu ? "/matcher" : "/en/matcher"} className={styles.toolCard}>
              <span className={styles.toolKicker}>01 · ROUTE MATCHER</span>
              <h3 className={styles.toolTitle}>{isRu ? "Подобрать программу" : "Match Program"}</h3>
              <p className={styles.toolDesc}>
                {isRu
                  ? "Локальный подбор направления без отправки данных на сервер."
                  : "Local route recommendation calculated strictly in-browser."}
              </p>
            </Link>

            <Link href={isRu ? "/business" : "/en/business"} className={styles.toolCard}>
              <span className={styles.toolKicker}>02 · CAPACITY SIMULATOR</span>
              <h3 className={styles.toolTitle}>{isRu ? "Калькулятор команды" : "Capacity Simulator"}</h3>
              <p className={styles.toolDesc}>
                {isRu
                  ? "Оценка высвобождаемого времени сотрудников по 4 параметрам."
                  : "Estimate recoverable team hours using transparent sensitivity models."}
              </p>
            </Link>

            <Link href={isRu ? "/proof" : "/en/proof"} className={styles.toolCard}>
              <span className={styles.toolKicker}>03 · BRIEF COMPILER</span>
              <h3 className={styles.toolTitle}>{isRu ? "Собрать brief" : "Compile Brief"}</h3>
              <p className={styles.toolDesc}>
                {isRu
                  ? "Генератор структурированного запроса для старта обучения."
                  : "Generate structured task definitions ready for human review."}
              </p>
            </Link>
          </div>

          <div className={styles.formulaBox}>
            <span className={styles.toolKicker}>{isRu ? "Открытая формула расчета (Sensitivity Scenario)" : "Open Sensitivity Formula"}</span>
            <pre className={styles.formulaCode}>
              {`monthlyHours = team * weeklyHours * (52 / 12)\nrecoverableHours = monthlyHours * (recoverablePercent / 100)\ngrossMonthlyValue = recoverableHours * hourlyRate`}
            </pre>
            <p className={styles.formulaNote}>
              {isRu
                ? "NOT an ROI forecast · NOT an automated financial promise · Model sensitivity scenario only."
                : "NOT an ROI forecast · NOT an automated financial promise · Model sensitivity scenario only."}
            </p>
          </div>
        </section>

        {/* ----------------------------------------------------
            FAQ SECTION
            ---------------------------------------------------- */}
        <section className={styles.sectionWhite} id="faq">
          <div className={styles.faqGrid}>
            <div className={styles.sectionHeader}>
              <span className={styles.sectionKicker}>FAQ</span>
              <h2>{isRu ? "Коротко о главном" : "The essentials"}</h2>
            </div>

            <div className={styles.faqList}>
              <details className={styles.faqItem}>
                <summary className={styles.faqSummary}>
                  <span>{isRu ? "Нужно ли уметь программировать?" : "Do I need to know how to code?"}</span>
                  <span aria-hidden="true">+</span>
                </summary>
                <p className={styles.faqAnswer}>
                  {isRu
                    ? "Нет. Базовые программы начинаются без кода. Технический стек подключаем только там, где он нужен для вашей цели."
                    : "No. Core programs can start without code. Technical tools are introduced only when they serve the learner's goal."}
                </p>
              </details>

              <details className={styles.faqItem}>
                <summary className={styles.faqSummary}>
                  <span>{isRu ? "Это записанный курс?" : "Is this a recorded course?"}</span>
                  <span aria-hidden="true">+</span>
                </summary>
                <p className={styles.faqAnswer}>
                  {isRu
                    ? "Нет. Основа — персональная работа 1-на-1 и практика на ваших задачах. Материалы и шаблоны остаются после занятий."
                    : "No. The core format is one-to-one, project-based work. Templates and project materials stay with the learner."}
                </p>
              </details>

              <details className={styles.faqItem}>
                <summary className={styles.faqSummary}>
                  <span>{isRu ? "Какие AI-инструменты используются?" : "Which AI tools do you teach?"}</span>
                  <span aria-hidden="true">+</span>
                </summary>
                <p className={styles.faqAnswer}>
                  {isRu
                    ? "Подбираем инструменты под задачу, а не строим обучение вокруг одного бренда. Важнее переносимый навык постановки задачи, проверки и сборки процесса."
                    : "Tools are selected by task. The objective is a transferable method for specifying, verifying and building — not dependency on one interface."}
                </p>
              </details>

              <details className={styles.faqItem}>
                <summary className={styles.faqSummary}>
                  <span>{isRu ? "Можно ли учить ребёнка или подростка?" : "Can children and teenagers join?"}</span>
                  <span aria-hidden="true">+</span>
                </summary>
                <p className={styles.faqAnswer}>
                  {isRu
                    ? "Да. Для 8–13 и 14–18 есть отдельные траектории. Контакт и заявку оставляет взрослый; возрастные требования конкретных сервисов проверяются перед использованием."
                    : "Yes. Ages 8–13 and 14–18 have separate tracks. Applications and contact details for minors are handled by an adult."}
                </p>
              </details>

              <details className={styles.faqItem}>
                <summary className={styles.faqSummary}>
                  <span>{isRu ? "Что будет на выходе?" : "What is the output?"}</span>
                  <span aria-hidden="true">+</span>
                </summary>
                <p className={styles.faqAnswer}>
                  {isRu
                    ? "Не сертификат ради сертификата, а законченный результат: процесс, исследование, ассистент, презентация, мини-продукт или портфолио-проект."
                    : "A finished artifact: a workflow, research brief, assistant, presentation, mini-product or portfolio project — not attendance alone."}
                </p>
              </details>
            </div>
          </div>
        </section>
      </main>

      {/* ----------------------------------------------------
          DARK FOOTER
          ---------------------------------------------------- */}
      <footer className={styles.footer} data-dark="1">
        <div className={styles.footerGrid}>
          <div className={styles.instructorBlock}>
            <span className={styles.instructorKicker}>HUMAN IN THE LOOP · STATED</span>
            <h3 className={styles.instructorTitle}>{isRu ? "Роберт · founder / instructor" : "Robert · founder / instructor"}</h3>
            <p className={styles.instructorBio}>
              {isRu
                ? "Я строю и использую AI-системы в реальной работе: research-процессы, agents, automation, decision workflows и цифровые продукты. На занятиях мы разбираем задачу, собираем решение, тестируем и исправляем слабые места."
                : "I build and use AI systems in real work: research workflows, agents, automation, decision workflows and digital products. Sessions use real tasks: define, build, test and fix weak points."}
            </p>
          </div>

          <div className={styles.footerCol}>
            <h3 className={styles.footerColTitle}>{isRu ? "Направления" : "Tracks"}</h3>
            <ul className={styles.footerLinks}>
              <li><Link href={isRu ? "/personal" : "/en/personal"}>{isRu ? "Взрослые 1-на-1" : "Adults 1:1"}</Link></li>
              <li><Link href={isRu ? "/kids" : "/en/kids"}>{isRu ? "Дети 8–13" : "Kids 8–13"}</Link></li>
              <li><Link href={isRu ? "/teens" : "/en/teens"}>{isRu ? "Подростки 14–18" : "Teens 14–18"}</Link></li>
              <li><Link href={isRu ? "/business" : "/en/business"}>{isRu ? "Команды и бизнес" : "Teams & Business"}</Link></li>
            </ul>
          </div>

          <div className={styles.footerCol}>
            <h3 className={styles.footerColTitle}>{isRu ? "Система и пруф" : "System & Proof"}</h3>
            <ul className={styles.footerLinks}>
              <li><Link href={isRu ? "/proof" : "/en/proof"}>Proof Lab</Link></li>
              <li><Link href={isRu ? "/studio" : "/en/studio"}>AI Studio</Link></li>
              <li><Link href={isRu ? "/method" : "/en/method"}>{isRu ? "Метод" : "Method"}</Link></li>
              <li><Link href={isRu ? "/pricing" : "/en/pricing"}>{isRu ? "Стоимость" : "Pricing"}</Link></li>
            </ul>
          </div>

          <div className={styles.footerCol}>
            <h3 className={styles.footerColTitle}>{isRu ? "Документы" : "Legal & Privacy"}</h3>
            <ul className={styles.footerLinks}>
              <li><Link href={isRu ? "/privacy" : "/en/privacy"}>{isRu ? "Приватность" : "Privacy"}</Link></li>
              <li><Link href={isRu ? "/terms" : "/en/terms"}>{isRu ? "Условия" : "Terms"}</Link></li>
              <li><Link href={isRu ? "/safety" : "/en/safety"}>{isRu ? "Безопасность" : "Safety"}</Link></li>
              <li><Link href={isRu ? "/about" : "/en/about"}>{isRu ? "О проекте" : "About"}</Link></li>
            </ul>
          </div>
        </div>

        <div className={styles.footerBottom}>
          <span>© 2026 AI Skill Lab · online / Phuket</span>
          <span>R74 LIVE VERIFIED · EXACT QUALIFIED PREVIEW BOUND</span>
        </div>
      </footer>
    </div>
  );
}