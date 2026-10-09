import type { Metadata } from "next";
import { WorkshopEditorial } from "@/components/workshop/WorkshopEditorial";
import Link from "next/link";
export const metadata: Metadata = {
  title: { absolute: "Build Log: разработка с ИИ — AI Skill Lab · Пхукет" },
  description: "Открытый build log AI Skill Lab: реальные итерации, ошибки, AI-роль, human gates, автоматические проверки и release engineering.",
  alternates: { canonical: "/build", languages: { ru: "/build", en: "/en/build" } },
};

const milestones = [
  ["R8", "BASELINE", "Контур проверки и родительских решений", "Проект получил первый переносимый источник истины и прозрачную систему проверки без фальшивых отзывов и обещаний."],
  ["R24", "COMMERCIAL", "Соответствие коммерческих условий", "Цены, пакеты и формулировки сведены к единой утверждённой версии и защищены автоматической проверкой соответствия."],
  ["R31", "ВЫПОЛНЕНИЕ", "Поведение, не разметка", "После синтаксической ошибки в статическом подборе программы появились проверки поведения, запасной вариант без JavaScript и проверяемый путь записи."],
  ["R38", "УПРАВЛЕНИЕ", "Безопасность и структурированные данные", "CSP на основе хешей, требования приватности, целостность метаданных и структурированных данных, а также проверки соответствия исходников статике стали частью процесса выпуска."],
  ["R49", "ВЫПУСК", "Воспроизводимая сборка", "Артефакт выпуска, манифест и архив стали собираться и восстанавливаться побайтно вместо ручной упаковки."],
  ["R60", "ОПЫТ", "Сайт как демонстрация", "Примеры и проверка, примеры проектов, симулятор пилота, составление задачи, задание и граф навыков превратили сайт в интерактивную демонстрацию."],
  ["R65", "ATTENTION", "Первый экран продукта", "Первый экран перестал быть маркетинговой иллюстрацией и начал показывать активный процесс: задача → сборка → проверка → запуск."],
  ["R66", "ПРОИСХОЖДЕНИЕ", "Открытая история сборки", "История сборки, ошибки, инструменты и границы ответственности становятся частью самого продукта."],
  ["R68", "ПЕРЕДАЧА", "Скорость как проверяемое требование", "Размер первого экрана в худшем случае составляет около 14 КБ Brotli: HTML, общий CSS и сценарий инструментов. Бюджет проверяется при каждом выпуске."],
] as const;

const failures = [
  ["ОШИБКА СКРИПТА", "В статической версии подбора программы была синтаксическая ошибка.", "Добавили синтаксическую проверку и быструю проверку поведения."],
  ["РАСХОЖДЕНИЕ МЕТАДАННЫХ", "Русская и английская версии, а также исходники и статика расходились в метаданных для поиска и соцсетей.", "Добавили воспроизводимые метаданные, hreflang и проверку структурированных данных."],
  ["ПОВРЕЖДЁН АРХИВ", "Один архив выпуска оказался повреждённым.", "Появился сборщик, который проверяет SHA архива и манифеста и побайтное восстановление."],
  ["ПРОПАЛА РАБОЧАЯ СРЕДА", "Рабочая директория однажды исчезла во время итерации.", "Проект восстановили из архивной копии Git. Непрерывность работы стала проверенной практикой, а не обещанием."],
  ["ВЫПУСК ЗАБЛОКИРОВАН", "Vercel quota / provider blockers мешали выпуску.", "Исходники, сборка, развёртывание и повторная проверка оставались разными состояниями. Блокер не выдавался за успешный результат."],
] as const;

export default function BuildPage() {
  return <WorkshopEditorial locale="ru" alternateHref="/en/build"><main id="main" className="proofPage">
    <section className="proofHero"><div className="shell proofHeroGrid"><div>
      <span className="proofEyebrow"><i/> КАК СДЕЛАН САЙТ / ОТКРЫТАЯ ИСТОРИЯ</span>
      <h1>Этот сайт —<br/><em>наш собственный кейс.</em></h1>
      <p>Не «сделано с ИИ» как наклейка. Ниже — реальная история итераций: что ускорял ИИ, что оставалось человеческим решением, какие ошибки нашли и какие проверки появились после них.</p>
      <div className="heroActions"><a className="button buttonLight" href="#timeline">Смотреть историю сборки ↓</a><a className="button buttonGhost buttonOnDark" href="/_release.json">Текущий манифест ↗</a></div>
    </div><div className="proofConsole" aria-label="Build provenance console"><div className="proofConsoleTop"><span>AI SKILL LAB / BUILD PROVENANCE</span><b className="statusDot">EVIDENCE-SCOPED</b></div><div className="proofConsoleBody"><p><span>01</span><b>ai_role</b><strong>ACCELERATE</strong></p><p><span>02</span><b>human_role</b><strong>DECIDE</strong></p><p><span>03</span><b>machine_role</b><strong>VERIFY</strong></p><p><span>04</span><b>claims</b><strong>BOUNDED</strong></p><p><span>05</span><b>history</b><strong>PORTABLE</strong></p><p><span>06</span><b>release</b><strong>MANIFESTED</strong></p></div><div className="proofConsoleFoot"><span>IDEA</span><i/><span>ITERATE</span><i/><span>BREAK</span><i/><span>PROVE</span></div></div></div></section>

    <section className="section" id="timeline"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">Этапы сборки</span><h2>Не один промпт.<br/><em>Система итераций.</em></h2></div><p>Это снимок основных этапов, а не полный журнал изменений. Точный идентификатор текущего выпуска всегда указан в <code>/_release.json</code>.</p></div><div className="programGrid">{milestones.map(([r,meta,title,text],i)=><article className="programCard" key={r}><span className="cardIndex">{String(i+1).padStart(2,"0")}</span><div className="cardSpacer"/><span className="cardMeta">{r} · {meta}</span><h3>{title}</h3><p>{text}</p></article>)}</div></div></section>

    <section className="proofSplit"><div className="shell proofSplitGrid"><article><span className="kicker">Что сделал ИИ</span><h2>Искал,<br/>генерировал,<br/>ускорял.</h2><ul><li>исследовал варианты и актуальные правила</li><li>предлагал архитектуру, тексты и код</li><li>выявлял расхождения между исходниками и статическими страницами</li><li>создавал тестовую обвязку и инструменты выпуска</li></ul></article><article className="proofHuman"><span className="kicker kickerLight">За что отвечал человек</span><h2>Выбирал,<br/>ограничивал,<br/>разрешал.</h2><ul><li>определял продуктовую цель и коммерческую правду</li><li>принимал визуальные и смысловые решения</li><li>задавал границы риска, подтверждаемых утверждений и безопасности детей</li><li>сохранял окончательное право разрешить выпуск в рабочую среду</li></ul></article></div></section>

    <section className="section sectionInk"><div className="shell"><div className="sectionHead splitHead sectionHeadLight"><div><span className="kicker kickerLight">Фактические инструменты</span><h2>Только то,<br/><em>что реально использовали.</em></h2></div><p>Планируемые инструменты не записываются в кейс задним числом. Если новый агент или сервис подключится позже, это будет отдельная проверяемая итерация.</p></div><div className="proofGateGrid"><article><span>01</span><h3>CHATGPT</h3><p>Продуктовые рассуждения, исследование и синтез, подготовка кода, проверка дизайна и итерационная работа.</p></article><article><span>02</span><h3>WEB ИССЛЕДОВАНИЕ</h3><p>Проверка актуальных правил и сравнение современных продуктовых и дизайн-подходов.</p></article><article><span>03</span><h3>ЛОКАЛЬНЫЕ ПРОВЕРКИ</h3><p>Проверки на Python и Node, быстрая проверка поведения, хеши CSP, соответствие метаданных и манифест выпуска.</p></article><article><span>04</span><h3>GIT / BUNDLES</h3><p>Точная история, clean точки проверки и переносимое восстановление проекта.</p></article><article><span>05</span><h3>VERCEL</h3><p>Целевое развёртывание. Предпросмотр, рабочая среда и проверка результата — отдельные этапы выпуска.</p></article><article><span>06</span><h3>ПРОВЕРКА ЧЕЛОВЕКОМ</h3><p>Цель, вкус, фактические утверждения, границы риска и финальное решение о выпуске.</p></article><article><span>07</span><h3>CLAUDE</h3><p>Аудит и замеры живого сайта, проверка фактов по первоисточникам, спецификации задач для исполнителя. Claude Дизайн — дизайн-система «Мастерская»: палитра, типографика, знак.</p></article></div></div></section>

    <section className="section"><div className="shell"><div className="sectionHead splitHead"><div><span className="kicker">Журнал сбоев</span><h2>Сильнее всего<br/>система выросла на ошибках.</h2></div><p>Мы не прячем ошибки из случай учёба. Полезная ошибка должна менять систему так, чтобы её класс больше не проходил незамеченным.</p></div><div className="programGrid">{failures.map(([title,problem,fix],i)=><article className="programCard" key={title}><span className="cardIndex">0{i+1}</span><div className="cardSpacer"/><span className="cardMeta">СБОЙ → КОНТРОЛЬ</span><h3>{title}</h3><p>{problem}</p><p><strong>→ {fix}</strong></p></article>)}</div></div></section>

    <section className="section sectionMuted"><div className="shell proofHonesty"><div><span className="kicker">Что это доказывает</span><h2>Не «ИИ сделал сайт».<br/><em>Мы умеем управлять ИИ-сборкой.</em></h2></div><div><p>Доказательство не в количестве сгенерированных строк. Оно в том, что продукт можно развивать, проверять, восстанавливать, ограничивать и выпускать без потери коммерческой и смысловой правды.</p><p>Это та же дисциплина, которую мы продаём в обучении и ИИ-проектах: <strong>Задача → Сборка → Проверка → Запуск.</strong></p><div className="heroActions"><Link className="button buttonPrimary" href="/proof">Открыть примеры и проверку →</Link><Link className="textLink" href="/projects">Примеры проектов →</Link></div></div></div></section>
  </main></WorkshopEditorial>;
}
