import type { Metadata } from "next";
import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

export const metadata: Metadata = {
  title: "Build Log — как AI Skill Lab построен с AI",
  description: "Открытый build log AI Skill Lab: реальные итерации, ошибки, AI-роль, human gates, автоматические проверки и release engineering.",
  alternates: { canonical: "/build", languages: { ru: "/build", en: "/en/build" } },
};

const milestones = [
  ["R8", "BASELINE", "Proof + parent decision layer", "Проект получил первую переносимую source authority и честный proof-контур без фальшивых отзывов и обещаний."],
  ["R24", "COMMERCIAL", "Commercial parity", "Цены, пакеты и формулировки были сведены в единую коммерческую правду и защищены автоматическим parity gate."],
  ["R31", "RUNTIME", "Behavior, not markup", "После реального syntax-багa static matcher появились runtime smoke-tests, no-JS fallback и проверяемый Start flow."],
  ["R38", "GOVERNANCE", "Security + structured data", "Hashed CSP, privacy contract, metadata/structured-data integrity и source/static semantic gates стали частью release-системы."],
  ["R49", "RELEASE", "Deterministic builder", "Release artifact, manifest и wrapper стали собираться и восстанавливаться byte-for-byte вместо ручной упаковки."],
  ["R60", "EXPERIENCE", "Site becomes the demo", "Proof Lab, Project Studio, Pilot Simulator, Brief Compiler, Challenge и Skill Graph превратили сайт в интерактивное доказательство."],
  ["R65", "ATTENTION", "Product-scene hero", "Первый экран перестал быть маркетинговой иллюстрацией и начал показывать ACTIVE WORKFLOW → DEFINE → BUILD → VERIFY → SHIP."],
  ["R66", "PROVENANCE", "Build process becomes public", "История сборки, failures, toolchain и границы ответственности становятся частью самого продукта."],
] as const;

const failures = [
  ["STATIC JS BROKE", "Matcher имел синтаксическую ошибку в deployable static.", "Добавили syntax gate + behavioral runtime smoke."],
  ["METADATA DRIFT", "RU/EN и source/static расходились по social/SEO metadata.", "Добавили deterministic metadata, hreflang и structured-data gates."],
  ["WRAPPER CORRUPTED", "Один release-wrapper оказался повреждённым.", "Появился builder, который проверяет archive SHA, manifest SHA и byte-exact reconstruction."],
  ["SANDBOX DISAPPEARED", "Рабочая директория однажды исчезла во время итерации.", "Exact проект восстановили из Git bundle. Continuity стала проверенной практикой, не обещанием."],
  ["DEPLOYMENT BLOCKED", "Vercel quota / provider blockers мешали выпуску.", "Source, build, deployment и readback остались разными состояниями. Блокер не выдавался за PASS."],
] as const;

export default function BuildPage() {
  return <><Header alternateHref="/en/build"/><main id="main" className="proofPage">
    <section className="proofHero"><div className="shell proofHeroGrid"><div>
      <span className="proofEyebrow"><i/> BUILD STORY / OPEN PROVENANCE</span>
      <h1>Этот сайт —<br/><em>наш собственный кейс.</em></h1>
      <p>Не «сделано с AI» как наклейка. Ниже — реальная история итераций: что ускорял AI, что оставалось человеческим решением, какие ошибки нашли и какие проверки появились после них.</p>
      <div className="heroActions"><a className="button buttonLight" href="#timeline">Смотреть build log ↓</a><a className="button buttonGhost buttonOnDark" href="/_release.json">Текущий manifest ↗</a></div>
    </div><div className="proofConsole" aria-label="Build provenance console"><div className="proofConsoleTop"><span>AI SKILL LAB / BUILD PROVENANCE</span><b>● EVIDENCE-SCOPED</b></div><div className="proofConsoleBody"><p><span>01</span><b>ai_role</b><strong>ACCELERATE</strong></p><p><span>02</span><b>human_role</b><strong>DECIDE</strong></p><p><span>03</span><b>machine_role</b><strong>VERIFY</strong></p><p><span>04</span><b>claims</b><strong>BOUNDED</strong></p><p><span>05</span><b>history</b><strong>PORTABLE</strong></p><p><span>06</span><b>release</b><strong>MANIFESTED</strong></p></div><div className="proofConsoleFoot"><span>IDEA</span><i/><span>ITERATE</span><i/><span>BREAK</span><i/><span>PROVE</span></div></div></div></section>

    <section className="section" id="timeline"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">Build timeline</span><h2>Не один промпт.<br/><em>Система итераций.</em></h2></div><p>Это milestone snapshot, а не полный changelog. Exact identity текущего release всегда лежит в <code>/_release.json</code>.</p></div><div className="programGrid">{milestones.map(([r,meta,title,text],i)=><article className="programCard" key={r}><span className="cardIndex">{String(i+1).padStart(2,"0")}</span><div className="cardSpacer"/><span className="cardMeta">{r} · {meta}</span><h3>{title}</h3><p>{text}</p></article>)}</div></div></section>

    <section className="proofSplit"><div className="shell proofSplitGrid"><article><span className="kicker">AI did</span><h2>Искал,<br/>генерировал,<br/>ускорял.</h2><ul><li>исследовал варианты и актуальные правила</li><li>предлагал архитектуру, тексты и код</li><li>искал source/static расхождения</li><li>создавал тестовую и release-обвязку</li></ul></article><article className="proofHuman"><span className="kicker kickerLight">Human owned</span><h2>Выбирал,<br/>ограничивал,<br/>разрешал.</h2><ul><li>определял продуктовую цель и коммерческую правду</li><li>принимал визуальные и смысловые решения</li><li>задавал risk / claims / youth-safety границы</li><li>держал финальное право на production release</li></ul></article></div></section>

    <section className="section sectionInk"><div className="shell"><div className="sectionHead splitHead sectionHeadLight"><div><span className="kicker kickerLight">Actual toolchain</span><h2>Только то,<br/><em>что реально использовали.</em></h2></div><p>Планируемые инструменты не записываются в кейс задним числом. Если новый агент или сервис подключится позже, это будет отдельная проверяемая итерация.</p></div><div className="proofGateGrid"><article><span>01</span><h3>CHATGPT</h3><p>Product reasoning, research synthesis, code drafting, QA design и итерационная работа.</p></article><article><span>02</span><h3>WEB RESEARCH</h3><p>Актуальные policy-проверки и сравнение современных product/design patterns.</p></article><article><span>03</span><h3>LOCAL TEST STACK</h3><p>Python + Node gates, runtime smoke, CSP hashes, metadata parity и release manifest.</p></article><article><span>04</span><h3>GIT / BUNDLES</h3><p>Точная история, clean checkpoints и переносимое восстановление проекта.</p></article><article><span>05</span><h3>VERCEL</h3><p>Deployment target. Preview, production и readback считаются отдельными release gates.</p></article><article><span>06</span><h3>HUMAN REVIEW</h3><p>Цель, вкус, фактические claims, risk boundaries и финальное решение о выпуске.</p></article></div></div></section>

    <section className="section"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">Failure log</span><h2>Сильнее всего<br/>система выросла на ошибках.</h2></div><p>Мы не прячем failures из case study. Полезная ошибка должна менять систему так, чтобы её класс больше не проходил незамеченным.</p></div><div className="programGrid">{failures.map(([title,problem,fix],i)=><article className="programCard" key={title}><span className="cardIndex">0{i+1}</span><div className="cardSpacer"/><span className="cardMeta">FAILURE → CONTROL</span><h3>{title}</h3><p>{problem}</p><p><strong>→ {fix}</strong></p></article>)}</div></div></section>

    <section className="section sectionMuted"><div className="shell proofHonesty"><div><span className="kicker">Что это доказывает</span><h2>Не «AI сделал сайт».<br/><em>Мы умеем управлять AI-сборкой.</em></h2></div><div><p>Доказательство не в количестве сгенерированных строк. Оно в том, что продукт можно развивать, проверять, восстанавливать, ограничивать и выпускать без потери коммерческой и смысловой правды.</p><p>Это та же дисциплина, которую мы продаём в обучении и AI-проектах: <strong>Define → Build → Verify → Ship.</strong></p><div className="heroActions"><Link className="button buttonPrimary" href="/proof">Открыть Proof Lab →</Link><Link className="textLink" href="/projects">Project Studio →</Link></div></div></div></section>
  </main><Footer/></>;
}
