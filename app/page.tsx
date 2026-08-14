import Link from "next/link";
import { ArrowIcon } from "@/components/ArrowIcon";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { LeadForm } from "@/components/LeadForm";

const programs = [
  {
    index: "01",
    title: "AI для жизни и работы",
    text: "От уверенной работы с моделями до исследований, контента, анализа и личных AI-процессов.",
    meta: "1-на-1 · с нуля",
  },
  {
    index: "02",
    title: "AI Builder",
    text: "Создание собственных ассистентов, автоматизаций и рабочих связок без лишней теории.",
    meta: "Практика · проекты",
  },
  {
    index: "03",
    title: "AI для бизнеса",
    text: "Разбираем реальные процессы команды и внедряем AI там, где он экономит время или усиливает результат.",
    meta: "Команды · процессы",
  },
];

const faq = [
  ["Нужно ли уметь программировать?", "Нет. Базовые программы начинаются без кода. Если цель — создавать более сложные системы, постепенно подключаем технический стек."],
  ["Это записанный курс?", "Нет. Основа — персональные занятия и практика на ваших задачах. Материалы и шаблоны остаются у вас после занятий."],
  ["Какие AI-инструменты используются?", "Подбираем инструменты под задачу: ChatGPT, Gemini, Claude и другие актуальные сервисы. Цель — не привязать ученика к одному интерфейсу, а научить переносимому подходу."],
  ["Как проходит обучение детей?", "Отдельная программа строится вокруг проектов, критического мышления и безопасного использования AI. Заявку и контакт оставляет родитель."],
];

export default function Home() {
  return (
    <>
      <Header />
      <main>
        <section className="hero">
          <div className="orb orbOne" />
          <div className="orb orbTwo" />
          <div className="shell heroGrid">
            <div className="heroCopy">
              <div className="eyebrow"><span className="dot" /> Персональное обучение AI</div>
              <h1>Не курс про AI.<br /><span>Навык работать с ним.</span></h1>
              <p className="heroLead">
                Учимся применять искусственный интеллект к реальным задачам — от первых промптов до собственных автоматизаций и проектов.
              </p>
              <div className="heroActions">
                <Link className="button buttonPrimary" href="#contact">Подобрать программу <ArrowIcon /></Link>
                <Link className="textLink" href="#programs">Смотреть направления <ArrowIcon /></Link>
              </div>
              <div className="heroStats">
                <div><strong>1:1</strong><span>индивидуальный формат</span></div>
                <div><strong>80%</strong><span>практика и проекты</span></div>
                <div><strong>4</strong><span>траектории обучения</span></div>
              </div>
            </div>
            <div className="heroVisual" aria-label="Схема обучения AI">
              <div className="visualTop"><span>YOUR AI STACK</span><span className="livePill">● LIVE</span></div>
              <div className="visualCore">
                <div className="coreRing ring1" />
                <div className="coreRing ring2" />
                <div className="coreCenter">AI</div>
                <div className="node nodeA">RESEARCH</div>
                <div className="node nodeB">CREATE</div>
                <div className="node nodeC">AUTOMATE</div>
                <div className="node nodeD">THINK</div>
              </div>
              <div className="visualBottom">
                <div><span>01</span><b>ЗАДАЧА</b></div>
                <i />
                <div><span>02</span><b>ИНСТРУМЕНТ</b></div>
                <i />
                <div><span>03</span><b>РЕЗУЛЬТАТ</b></div>
              </div>
            </div>
          </div>
        </section>

        <section className="section" id="programs">
          <div className="shell">
            <div className="sectionHead splitHead">
              <div>
                <span className="kicker">Направления</span>
                <h2>Под задачу, а не под шаблон</h2>
              </div>
              <p>Одна база, разные траектории: каждый ученик собирает свой набор AI-навыков вокруг конкретной цели.</p>
            </div>
            <div className="programGrid">
              {programs.map((program) => (
                <article className="programCard" key={program.index}>
                  <span className="cardIndex">{program.index}</span>
                  <div className="cardSpacer" />
                  <span className="cardMeta">{program.meta}</span>
                  <h3>{program.title}</h3>
                  <p>{program.text}</p>
                  <Link href="#contact" className="cardLink">Подробнее <ArrowIcon /></Link>
                </article>
              ))}
              <article className="programCard kidsCard">
                <div className="kidsBadge">8–14</div>
                <div className="cardSpacer" />
                <span className="cardMeta">Отдельная программа</span>
                <h3>AI для детей</h3>
                <p>Учимся создавать, исследовать и думать вместе с AI — безопасно, понятно и через собственные проекты.</p>
                <Link href="/kids" className="cardLink">Открыть программу <ArrowIcon /></Link>
              </article>
            </div>
          </div>
        </section>

        <section className="kidsBand">
          <div className="shell kidsBandGrid">
            <div>
              <span className="kicker kickerLight">Для нового поколения</span>
              <h2>Ребёнок не просто нажимает «спросить AI».<br />Он понимает, <em>что с ним делать.</em></h2>
              <p>Для детей 8–14 лет: изображения, истории, исследования, презентации, первые игры и проекты. Отдельно — фактчекинг, приватность и правила работы с AI.</p>
              <Link className="button buttonLight" href="/kids">Программа для детей <ArrowIcon /></Link>
            </div>
            <div className="kidsManifesto">
              <span>CREATE</span><span>QUESTION</span><span>CHECK</span><span>BUILD</span>
              <div className="manifestoCore">AI<br /><small>IS A TOOL</small></div>
            </div>
          </div>
        </section>

        <section className="section" id="format">
          <div className="shell">
            <div className="sectionHead">
              <span className="kicker">Как это работает</span>
              <h2>От цели до собственного результата</h2>
            </div>
            <div className="steps">
              <article><span>01</span><h3>Диагностика</h3><p>Определяем текущий уровень, интересы и конкретный результат, ради которого вы пришли.</p></article>
              <article><span>02</span><h3>Персональный маршрут</h3><p>Собираем программу и инструменты без ненужных модулей и одинаковых домашних заданий для всех.</p></article>
              <article><span>03</span><h3>Практика</h3><p>Каждое занятие — работа руками. Учимся на реальных задачах и сразу собираем собственные шаблоны.</p></article>
              <article><span>04</span><h3>Проект</h3><p>В конце остаётся законченный результат: рабочий процесс, ассистент, исследование, презентация или другой проект.</p></article>
            </div>
          </div>
        </section>

        <section className="section sectionMuted" id="pricing">
          <div className="shell">
            <div className="sectionHead splitHead">
              <div><span className="kicker">Форматы</span><h2>Начать можно с малого</h2></div>
              <p>Цены первой версии. Программу можно скорректировать после вводного разговора.</p>
            </div>
            <div className="pricingGrid">
              <article className="priceCard">
                <span className="cardMeta">Start</span><h3>4 занятия</h3><div className="price">$390</div>
                <p>Чтобы разобраться в AI, настроить базовый рабочий процесс и понять, куда двигаться дальше.</p>
                <Link className="button buttonGhost buttonWide" href="#contact">Выбрать Start</Link>
              </article>
              <article className="priceCard featuredPrice">
                <span className="popular">Оптимально</span><span className="cardMeta">Personal</span><h3>10 занятий</h3><div className="price">$890</div>
                <p>Полная персональная траектория с практикой, материалами и итоговым проектом.</p>
                <Link className="button buttonPrimary buttonWide" href="#contact">Выбрать Personal</Link>
              </article>
              <article className="priceCard">
                <span className="cardMeta">Team</span><h3>Для бизнеса</h3><div className="price">по запросу</div>
                <p>Разбор процессов, обучение команды и внедрение AI-связок под ваши рабочие задачи.</p>
                <Link className="button buttonGhost buttonWide" href="#contact">Обсудить задачу</Link>
              </article>
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
              <span className="kicker kickerLight">Следующий шаг</span>
              <h2>Опишите цель.<br />Соберём маршрут.</h2>
              <p>Оставьте контакт и пару слов о задаче. Для детской программы заявку заполняет родитель.</p>
            </div>
            <LeadForm />
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
