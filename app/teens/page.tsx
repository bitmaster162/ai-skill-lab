import type { Metadata } from "next";
import Link from "next/link";
import { ArrowIcon } from "@/components/ArrowIcon";
import { ContactButtons } from "@/components/ContactButtons";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "AI для подростков 14–18 лет",
  description: "Персональное обучение AI для подростков 14–18 лет: исследования, портфолио, автоматизации, основы кода и собственный AI-проект.",
  alternates: { canonical: "/teens", languages: { ru: "/teens", en: "/en/teens" } },
};

const modules = [
  ["01", "AI literacy", "Как устроены современные модели, где они полезны и почему хороший ответ всё равно нужно проверять."],
  ["02", "Research system", "Поиск, источники, сравнение версий, аргументация и короткие аналитические выводы."],
  ["03", "Prompting as specification", "Не «магические промпты», а постановка задачи: контекст, критерии, ограничения и итерации."],
  ["04", "Create & present", "Тексты, визуалы, презентации и объяснение собственной работы без маскировки вклада AI."],
  ["05", "Code with AI", "Как читать, менять и проверять простой код с помощью AI, даже если программирование только начинается."],
  ["06", "Automation", "Связываем повторяемые шаги в понятный workflow и обсуждаем, где автоматизация опасна."],
  ["07", "AI product thinking", "Проблема, пользователь, сценарий, прототип и критерий полезности вместо «сделаем приложение ради приложения»."],
  ["08", "Portfolio build", "Собираем проект, фиксируем решения, источники, ограничения и собственный вклад."],
  ["09", "Stress-test", "Проверяем ошибки, edge cases, качество источников и то, что проект действительно работает."],
  ["10", "Demo & next step", "Презентация проекта и персональная карта следующего уровня: код, дизайн, research или automation."],
];

export default function TeensPage() {
  return (
    <>
      <Header contactHref="/start" alternateHref="/en/teens" />
      <main>
        <section className="teenHero">
          <div className="shell teenHeroGrid">
            <div>
              <div className="eyebrow eyebrowLight"><span className="dot dotLight" /> 14–18 лет · portfolio track</div>
              <h1>Не готовиться к будущему.<br /><span>Начать собирать его.</span></h1>
              <p>AI как прикладной навык: research, код, автоматизации, презентации и собственный проект, который можно показать, а не только описать.</p>
              <div className="heroActions"><Link className="button buttonLight" href="/start">Подобрать трек <ArrowIcon /></Link><Link className="textLink textLinkLight" href="#teen-program">Смотреть программу <ArrowIcon /></Link></div>
              <div className="heroProofRow heroProofLight"><span>RESEARCH</span><span>BUILD</span><span>PORTFOLIO</span><span>VERIFY</span></div>
            </div>
            <div className="teenTerminal" aria-label="Схема подросткового AI-проекта">
              <div className="terminalTop"><span>portfolio_project.ai</span><span>● ACTIVE</span></div>
              <div className="terminalLines"><span><i>01</i> DEFINE PROBLEM</span><span><i>02</i> RESEARCH SOURCES</span><span><i>03</i> BUILD PROTOTYPE</span><span><i>04</i> TEST OUTPUT</span><span><i>05</i> EXPLAIN DECISIONS</span></div>
              <div className="terminalOutput"><small>OUTPUT</small><b>PROJECT THAT CAN BE SHOWN.</b></div>
            </div>
          </div>
        </section>

        <section className="trustStrip trustStripDark">
          <div className="shell trustStripGrid"><div><b>1-на-1</b><span>Уровень под ученика</span></div><div><b>Portfolio first</b><span>Каждый блок работает на проект</span></div><div><b>Adult contact</b><span>Для несовершеннолетних</span></div><div><b>Responsible AI</b><span>Источники, авторство, приватность</span></div></div>
        </section>

        <section className="section" id="teen-program">
          <div className="shell">
            <div className="sectionHead splitHead"><div><span className="kicker">Программа</span><h2>10 модулей от AI literacy<br />до portfolio project</h2></div><p>Глубина зависит от стартового уровня. Сильный ученик быстрее переходит к коду и автоматизациям; новичок получает больше времени на базовую систему работы.</p></div>
            <div className="curriculumList teenCurriculum">
              {modules.map(([num, title, text]) => <article key={num}><span>{num}</span><h3>{title}</h3><p>{text}</p></article>)}
            </div>
          </div>
        </section>

        <section className="section sectionMuted">
          <div className="shell">
            <div className="sectionHead"><span className="kicker">Варианты проектов</span><h2>Не учебная имитация.<br />Небольшой, но настоящий результат.</h2></div>
            <div className="outcomeGrid outcomeGridLight">
              <article><span>01</span><h3>RESEARCH BRIEF</h3><p>Исследование темы с источниками, сравнением аргументов и визуальным выводом.</p></article>
              <article><span>02</span><h3>AI TOOL</h3><p>Простой помощник, workflow или автоматизация под понятную повторяемую задачу.</p></article>
              <article><span>03</span><h3>MINI PRODUCT</h3><p>Прототип сайта, приложения или интерактива с объяснением пользовательской задачи.</p></article>
              <article><span>04</span><h3>CREATIVE SYSTEM</h3><p>Проект на стыке дизайна, текста, видео или музыки с единым стилем и логикой.</p></article>
            </div>
          </div>
        </section>

        <section className="section">
          <div className="shell parentGrid">
            <div className="parentCard parentDark"><span className="kicker kickerLight">Для подростка</span><h2>Навык + портфолио</h2><ul className="checkList"><li>умение исследовать и проверять источники;</li><li>умение формулировать задачу как спецификацию;</li><li>первые навыки работы с кодом и автоматизациями;</li><li>законченный проект с понятным собственным вкладом;</li><li>карта следующего уровня после программы.</li></ul></div>
            <div className="parentCard"><span className="kicker">Для родителя</span><h2>Не «сидит в ChatGPT»</h2><ul className="checkList checkDark"><li>понятная цель программы до старта;</li><li>проектный прогресс вместо абстрактных оценок;</li><li>обсуждение цифровой приватности и авторства;</li><li>финальная презентация проекта;</li><li>контакт и организационные вопросы — через взрослого.</li></ul></div>
          </div>
        </section>

        <section className="section sectionMuted">
          <div className="shell">
            <div className="sectionHead splitHead"><div><span className="kicker">Стоимость</span><h2>Три уровня глубины</h2></div><p>Можно начать с короткого трека и перейти в Builder только если формат и интерес совпали.</p></div>
            <div className="pricingGrid">
              <article className="priceCard"><span className="cardMeta">Explorer</span><h3>6 занятий</h3><div className="price">$490</div><p>AI literacy + research + первый небольшой проект.</p><Link className="button buttonGhost buttonWide" href="/start">Выбрать Explorer</Link></article>
              <article className="priceCard featuredPrice"><span className="popular">Оптимально</span><span className="cardMeta">Portfolio</span><h3>10 занятий</h3><div className="price">$890</div><p>Полный маршрут с итоговым проектом и персональной картой развития.</p><Link className="button buttonPrimary buttonWide" href="/start">Выбрать Portfolio</Link></article>
              <article className="priceCard"><span className="cardMeta">Builder</span><h3>12 занятий</h3><div className="price">$1,290</div><p>Больше кода, автоматизаций и времени на технический или продуктовый проект.</p><Link className="button buttonGhost buttonWide" href="/start">Выбрать Builder</Link></article>
            </div>
          </div>
        </section>

        <section className="section safetyBand">
          <div className="shell safetyBandGrid">
            <div><span className="kicker">13–17 и AI-сервисы</span><h2>Разрешение взрослого — часть процесса.</h2></div>
            <div><p>Для несовершеннолетних организационный контакт остаётся у взрослого. У каждого AI-сервиса свои возрастные правила; для ChatGPT пользователям младше 18 требуется разрешение родителя или законного представителя.</p><Link className="textLink" href="/safety">Правила безопасности <ArrowIcon /></Link></div>
          </div>
        </section>

        <section className="contactSection" id="teens-contact">
          <div className="shell contactGrid"><div><span className="kicker kickerLight">Старт</span><h2>Расскажите, что уже интересно подростку.</h2><p>Код, дизайн, игры, наука, контент, бизнес или пока ничего конкретного — это достаточно, чтобы собрать первый маршрут.</p><ContactButtons fallbackHref="/start" /></div><div className="contactOnlyCard"><span className="cardMeta">Контакт взрослого</span><h3>Начните с цели и интересов</h3><p>Достаточно возраста, текущего уровня и направления интереса. Организационная переписка идёт через взрослого.</p><Link className="button buttonPrimary buttonWide" href="/start">Что написать →</Link></div></div>
        </section>
      </main>
      <Footer />
    </>
  );
}
