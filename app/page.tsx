import type { Metadata } from "next";
import Link from "next/link";
import { ArrowIcon } from "@/components/ArrowIcon";
import { ContactButtons } from "@/components/ContactButtons";
import { Footer } from "@/components/Footer";
import { JsonLd } from "@/components/JsonLd";
import { organizationSchema, websiteSchema } from "@/lib/structured-data";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  alternates: { canonical: "/", languages: { ru: "/", en: "/en" } },
};


const programs = [
  {
    index: "01",
    title: "AI для жизни и работы",
    text: "ChatGPT, Gemini, Claude и другие модели как рабочая система: исследования, тексты, анализ, решения и личные процессы.",
    meta: "1-на-1 · с нуля",
    href: "/start",
  },
  {
    index: "02",
    title: "AI Builder",
    text: "Ассистенты, автоматизации, агенты и простые AI-продукты. Меньше лекций — больше сборки руками.",
    meta: "Практика · проекты",
    href: "/start",
  },
  {
    index: "03",
    title: "AI для бизнеса",
    text: "Разбираем процессы команды, выбираем точки внедрения и обучаем сотрудников использовать AI измеримо и безопасно.",
    meta: "Команды · процессы",
    href: "/start",
  },
  {
    index: "04",
    title: "AI для детей",
    text: "8–13 лет: творчество, исследования, критическое мышление и собственный проект без модели «сделай за меня».",
    meta: "8–13 · родительский контакт",
    href: "/kids",
  },
  {
    index: "05",
    title: "AI для подростков",
    text: "14–18 лет: AI как реальный навык для учёбы, портфолио, первых проектов, кода и будущей профессии.",
    meta: "14–18 · portfolio track",
    href: "/teens",
  },
];

const outcomes = [
  ["PERSONAL OS", "Собственный набор AI-процессов для работы, учёбы или личных задач."],
  ["RESEARCH", "Исследование с источниками, проверкой фактов и структурированным выводом."],
  ["AI AGENT", "Рабочий ассистент или автоматизация под конкретный повторяемый процесс."],
  ["PORTFOLIO", "Законченный проект, который можно показать клиенту, школе, команде или родителю."],
];

const faq = [
  ["Нужно ли уметь программировать?", "Нет. Базовые программы начинаются без кода. Технический стек подключаем только там, где он нужен для вашей цели."],
  ["Это записанный курс?", "Нет. Основа — персональная работа 1-на-1 и практика на ваших задачах. Материалы и шаблоны остаются после занятий."],
  ["Какие AI-инструменты используются?", "Подбираем инструменты под задачу, а не строим обучение вокруг одного бренда. Важнее переносимый навык постановки задачи, проверки и сборки процесса."],
  ["Можно ли учить ребёнка или подростка?", "Да. Для 8–13 и 14–18 есть отдельные траектории. Контакт и заявку оставляет взрослый; возрастные требования конкретных сервисов проверяются перед использованием."],
  ["Что будет на выходе?", "Не сертификат ради сертификата, а законченный результат: процесс, исследование, ассистент, презентация, мини-продукт или портфолио-проект."],
];

export default function Home() {
  return (
    <>
      <JsonLd data={[websiteSchema, organizationSchema]} />
      <Header alternateHref="/en" />
      <main id="main">
        <section className="hero heroR2">
          <div className="orb orbOne" />
          <div className="orb orbTwo" />
          <div className="shell heroGrid">
            <div className="heroCopy">
              <div className="eyebrow"><span className="dot" /> Персональное обучение AI · online / Phuket</div>
              <h1>AI не должен<br />делать вас <span>зависимее.</span></h1>
              <p className="heroLead">
                Он должен делать вас сильнее. Учимся исследовать, создавать, автоматизировать и собирать собственные AI-процессы на реальных задачах.
              </p>
              <div className="heroActions">
                <Link className="button buttonPrimary" href="/start">Подобрать программу <ArrowIcon /></Link>
                <Link className="textLink" href="#programs">Смотреть направления <ArrowIcon /></Link>
              </div>
              <div className="heroProofRow">
                <span>1:1 PERSONAL</span><span>PROJECT-BASED</span><span>RU / EN</span><span>NO FLUFF</span>
              </div>
            </div>
            <div className="heroVisual" aria-label="Схема практического обучения AI">
              <div className="visualTop"><span>YOUR AI STACK</span><span className="livePill">● BUILD</span></div>
              <div className="visualCore">
                <div className="coreRing ring1" />
                <div className="coreRing ring2" />
                <div className="coreCenter">AI</div>
                <div className="node nodeA">RESEARCH</div>
                <div className="node nodeB">CREATE</div>
                <div className="node nodeC">AUTOMATE</div>
                <div className="node nodeD">VERIFY</div>
              </div>
              <div className="visualBottom">
                <div><span>01</span><b>ЦЕЛЬ</b></div><i />
                <div><span>02</span><b>СИСТЕМА</b></div><i />
                <div><span>03</span><b>РЕЗУЛЬТАТ</b></div>
              </div>
            </div>
          </div>
        </section>

        <section className="trustStrip">
          <div className="shell trustStripGrid">
            <div><b>Не массовый курс</b><span>Маршрут собирается под задачу</span></div>
            <div><b>Работа руками</b><span>Большая часть времени — практика</span></div>
            <div><b>Проверяемый результат</b><span>На выходе остаётся проект</span></div>
            <div><b>Responsible AI</b><span>Фактчекинг, приватность, границы</span></div>
          </div>
        </section>

        <section className="section" id="programs">
          <div className="shell">
            <div className="sectionHead splitHead">
              <div>
                <span className="kicker">5 траекторий</span>
                <h2>Один AI.<br />Совсем разные задачи.</h2>
              </div>
              <p>Не продаём одинаковую программу всем. Сначала определяем, какой результат должен появиться после обучения, затем собираем маршрут.</p>
            </div>
            <div className="programGrid programGridR2">
              {programs.map((program, index) => (
                <article className={`programCard ${index >= 3 ? "youthCard" : ""}`} key={program.index}>
                  <span className="cardIndex">{program.index}</span>
                  <div className="cardSpacer" />
                  <span className="cardMeta">{program.meta}</span>
                  <h3>{program.title}</h3>
                  <p>{program.text}</p>
                  <Link href={program.href} className="cardLink">Подробнее <ArrowIcon /></Link>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="section sectionInk">
          <div className="shell">
            <div className="sectionHead splitHead sectionHeadLight">
              <div><span className="kicker kickerLight">Что считается результатом</span><h2>Не «я посмотрел уроки».<br /><em>Я умею это делать.</em></h2></div>
              <p>Финальный проект выбирается под цель ученика. Ниже — типы результатов программы, а не выдуманные отзывы или обещания заработка.</p>
            </div>
            <div className="outcomeGrid">
              {outcomes.map(([title, text], index) => (
                <article key={title}><span>0{index + 1}</span><h3>{title}</h3><p>{text}</p></article>
              ))}
            </div>
          </div>
        </section>

        <section className="kidsBand kidsBandR2">
          <div className="shell kidsBandGrid">
            <div>
              <span className="kicker kickerLight">8–18 лет</span>
              <h2>Для детей — не «быстрее делать домашку».<br />Для подростков — <em>не просто промпты.</em></h2>
              <p>Две отдельные возрастные программы. 8–13 — через творчество, исследования и безопасные привычки. 14–18 — через реальные проекты, портфолио, код и AI-инструменты для учёбы и будущей работы.</p>
              <div className="heroActions">
                <Link className="button buttonLight" href="/kids">Дети 8–13 <ArrowIcon /></Link>
                <Link className="button buttonGhost buttonOnDark" href="/teens">Подростки 14–18 <ArrowIcon /></Link>
              </div>
            </div>
            <div className="ageSplitVisual">
              <div className="agePanel"><span>8–13</span><b>CREATE<br />QUESTION<br />CHECK</b><small>curiosity → project</small></div>
              <div className="agePanel agePanelAcid"><span>14–18</span><b>BUILD<br />RESEARCH<br />SHIP</b><small>skill → portfolio</small></div>
            </div>
          </div>
        </section>

        <section className="section" id="format">
          <div className="shell">
            <div className="sectionHead splitHead">
              <div><span className="kicker">Метод</span><h2>Цель → практика → система → проект</h2></div>
              <p>AI меняется слишком быстро, чтобы учить интерфейсы по кнопкам. Поэтому основа — переносимый способ работы, который остаётся полезным после очередного обновления модели.</p>
            </div>
            <div className="steps">
              <article><span>01</span><h3>Диагностика</h3><p>Фиксируем уровень, интересы, ограничения и конкретный результат.</p></article>
              <article><span>02</span><h3>Персональный маршрут</h3><p>Убираем лишние модули и выбираем только нужные инструменты.</p></article>
              <article><span>03</span><h3>Сборка руками</h3><p>Каждое занятие даёт артефакт: шаблон, исследование, workflow или часть проекта.</p></article>
              <article><span>04</span><h3>Финальный проект</h3><p>Ученик объясняет логику работы, ограничения AI и собственный вклад.</p></article>
            </div>
          </div>
        </section>

        <section className="section sectionMuted premiumParents">
          <div className="shell premiumParentGrid">
            <div className="premiumParentCopy">
              <span className="kicker">Premium Family</span>
              <h2>Не просто занятия ребёнку.<br />AI-среда для семьи.</h2>
              <p>Для родителей, которым нужен более управляемый формат: индивидуальный трек ребёнка, отдельные встречи со взрослым, настройка правил использования AI дома и финальная демонстрация проекта.</p>
              <ul className="featureList">
                <li>12 персональных занятий ребёнку или подростку</li>
                <li>2 отдельные сессии для родителя</li>
                <li>индивидуальная тема итогового проекта</li>
                <li>семейные правила приватности и использования AI</li>
                <li>финальная презентация результата</li>
              </ul>
            </div>
            <article className="premiumPriceCard">
              <span className="cardMeta">Family Concierge</span>
              <div className="price">$1,490</div>
              <p><strong>12 занятий + 2 сессии родителю</strong></p>
              <p>Премиальный персональный формат. Конкретный набор инструментов согласовывается с родителем и зависит от возраста.</p>
              <Link className="button buttonPrimary buttonWide" href="/start">Обсудить Family</Link>
              <small>Без скрытых подписок на обучение. Сторонние AI-сервисы, если нужны, оплачиваются отдельно.</small>
            </article>
          </div>
        </section>

        <section className="section" id="pricing">
          <div className="shell">
            <div className="sectionHead splitHead">
              <div><span className="kicker">Форматы</span><h2>Можно проверить формат<br />до большого пакета</h2></div>
              <p>Стоимость относится к персональному обучению 1-на-1. Детские и подростковые пакеты имеют собственные страницы.</p>
            </div>
            <div className="pricingGrid">
              <article className="priceCard">
                <span className="cardMeta">Start</span><h3>4 занятия</h3><div className="price">$390</div>
                <p>Разобраться в AI, настроить базовый рабочий процесс и получить первый полезный результат.</p>
                <Link className="button buttonGhost buttonWide" href="/start">Выбрать Start</Link>
              </article>
              <article className="priceCard featuredPrice">
                <span className="popular">Основной</span><span className="cardMeta">Personal</span><h3>10 занятий</h3><div className="price">$890</div>
                <p>Полная персональная траектория: практика, материалы, собственные шаблоны и итоговый проект.</p>
                <Link className="button buttonPrimary buttonWide" href="/start">Выбрать Personal</Link>
              </article>
              <article className="priceCard">
                <span className="cardMeta">Intensive</span><h3>12 занятий + проект</h3><div className="price">$1,290</div>
                <p>Для сложной задачи: автоматизация, AI-агент, мини-продукт или технический portfolio project.</p>
                <Link className="button buttonGhost buttonWide" href="/start">Выбрать Intensive</Link>
              </article>
            </div>
          </div>
        </section>

        <section className="section instructorSection">
          <div className="shell instructorGrid">
            <div className="instructorBadge"><span>HUMAN<br />IN THE<br />LOOP</span></div>
            <div>
              <span className="kicker">Роберт · founder / instructor</span>
              <h2>Обучение из практики,<br />а не из слайдов.</h2>
              <p>Я строю и использую AI-системы в реальной работе: research-процессы, agents, automation, decision workflows и цифровые продукты. На занятиях мы разбираем задачу, собираем решение, тестируем и исправляем слабые места.</p>
              <p className="finePrint">Без выдуманных клиентских логотипов, отзывов и обещаний дохода. Доказательство прогресса — результат, который ученик может показать и объяснить.</p>
              <div className="expertiseTags"><span>AI WORKFLOWS</span><span>AGENTS</span><span>RESEARCH</span><span>AUTOMATION</span><span>PRODUCT</span></div>
            </div>
          </div>
        </section>

        <section className="section" id="faq">
          <div className="shell faqGrid">
            <div className="sectionHead stickyHead"><span className="kicker">FAQ</span><h2>Коротко о главном</h2></div>
            <div className="faqList">
              {faq.map(([question, answer]) => (
                <details key={question}><summary>{question}<span>+</span></summary><p>{answer}</p></details>
              ))}
            </div>
          </div>
        </section>

        <section className="contactSection" id="contact">
          <div className="shell contactGrid">
            <div>
              <span className="kicker kickerLight">Старт · contact-only</span>
              <h2>Сначала задача.<br />Потом программа.</h2>
              <p>Напишите, для кого обучение и какой результат нужен. Для детей и подростков контакт должен принадлежать взрослому.</p>
              <ContactButtons fallbackHref="/start" />
            </div>
            <div className="contactOnlyCard">
              <span className="cardMeta">Короткий brief</span>
              <h3>Без формы и лишних данных</h3>
              <p>Укажите: кому обучение, цель, текущий уровень и формат online / Phuket. Для несовершеннолетнего достаточно возраста и интересов — без лишних персональных данных.</p>
              <Link className="button buttonPrimary buttonWide" href="/start">Что написать →</Link>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
