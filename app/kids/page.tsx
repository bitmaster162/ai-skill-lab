import type { Metadata } from "next";
import Link from "next/link";
import { ArrowIcon } from "@/components/ArrowIcon";
import { ContactButtons } from "@/components/ContactButtons";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "AI для детей 8–13 лет",
  description: "Персональная программа AI для детей 8–13 лет: творчество, исследования, критическое мышление, безопасная работа с AI и собственный итоговый проект.",
  alternates: { canonical: "/kids", languages: { ru: "/kids", en: "/en/kids" } },
};

const lessons = [
  ["01", "AI без магии", "Что AI умеет, чего не умеет и почему уверенный ответ может быть неправильным."],
  ["02", "Сильные вопросы", "Учимся давать контекст, задавать ограничения и улучшать результат итерациями."],
  ["03", "Персонажи и визуальные миры", "Создаём идеи, изображения и цельный визуальный стиль для собственного проекта."],
  ["04", "История вместе с AI", "Сюжет, герои, логика, редактура — AI помогает, но решения остаются у автора."],
  ["05", "AI-исследователь", "Ищем информацию, сравниваем источники и отделяем факт от красивой выдумки."],
  ["06", "Презентация, которую хочется смотреть", "Структурируем тему и превращаем материал в понятную визуальную историю."],
  ["07", "Логика и первые алгоритмы", "Разбираем задачу на шаги, пробуем простые сценарии и программное мышление."],
  ["08", "Мини-игра или интерактив", "Собираем небольшой проект с правилами, состояниями и обратной связью."],
  ["09", "Мой AI-проект", "Проектируем финальную работу: цель, план, материалы, проверка и улучшение."],
  ["10", "Демо-день", "Завершаем проект и учимся объяснять, что сделано самим, а где помогал AI."],
];

export default function KidsPage() {
  return (
    <>
      <Header contactHref="/start" alternateHref="/en/kids" />
      <main>
        <section className="kidsHero">
          <div className="shell kidsHeroGrid">
            <div>
              <div className="eyebrow eyebrowLight"><span className="dot dotLight" /> Для детей 8–13 лет · 1-на-1</div>
              <h1>AI — это не кнопка<br /><span>«сделай за меня».</span></h1>
              <p>Это инструмент, с которым ребёнок может придумывать, исследовать, создавать и — главное — учиться задавать хорошие вопросы и проверять ответы.</p>
              <div className="heroActions">
                <Link className="button buttonLight" href="/start">Обсудить с преподавателем <ArrowIcon /></Link>
                <Link className="textLink textLinkLight" href="#curriculum">Смотреть 10 занятий <ArrowIcon /></Link>
              </div>
              <div className="heroProofRow heroProofLight"><span>ADULT CONTACT</span><span>PRIVACY FIRST</span><span>PROJECT-BASED</span></div>
            </div>
            <div className="kidsHeroBoard">
              <div className="boardLabel">FINAL PROJECT</div>
              <div className="boardCanvas">
                <div className="boardCard bc1">IDEA<br /><b>→</b></div>
                <div className="boardCard bc2">RESEARCH<br /><b>→</b></div>
                <div className="boardCard bc3">CREATE<br /><b>→</b></div>
                <div className="boardCenter">MY<br />AI<br />PROJECT</div>
              </div>
              <div className="boardFoot"><span>10 LESSONS</span><span>REAL OUTPUT</span></div>
            </div>
          </div>
        </section>

        <section className="trustStrip trustStripDark">
          <div className="shell trustStripGrid">
            <div><b>45–60 минут</b><span>Под возраст и внимание</span></div>
            <div><b>1-на-1</b><span>Темп не диктует группа</span></div>
            <div><b>Контакт взрослого</b><span>Без прямого маркетинга ребёнку</span></div>
            <div><b>Свой проект</b><span>Ребёнок презентует результат сам</span></div>
          </div>
        </section>

        <section className="section">
          <div className="shell">
            <div className="sectionHead splitHead">
              <div><span className="kicker">Подход</span><h2>Не выращиваем зависимость от AI</h2></div>
              <p>Цель программы — чтобы ребёнок умел думать до запроса, проверять после ответа и понимал границы инструмента.</p>
            </div>
            <div className="kidsPrinciples">
              <article><span>01</span><h3>Сначала идея</h3><p>Ребёнок формулирует собственный замысел, а AI помогает его развить.</p></article>
              <article><span>02</span><h3>Проверять обязательно</h3><p>Разбираем ошибки и галлюцинации, сравниваем ответы с надёжными источниками.</p></article>
              <article><span>03</span><h3>Приватность по умолчанию</h3><p>Не вводим лишние персональные данные и обсуждаем цифровые границы до начала работы.</p></article>
              <article><span>04</span><h3>Проект важнее промпта</h3><p>Навык измеряется тем, что ребёнок способен придумать, собрать, объяснить и улучшить.</p></article>
            </div>
          </div>
        </section>

        <section className="section sectionMuted" id="curriculum">
          <div className="shell">
            <div className="sectionHead"><span className="kicker">Программа</span><h2>10 занятий → 1 законченный проект</h2><p className="sectionSub">Темы адаптируются под возраст и интересы: от космоса и животных до игр, искусства, музыки или техники.</p></div>
            <div className="curriculumList">
              {lessons.map(([num, title, text]) => (
                <article key={num}><span>{num}</span><h3>{title}</h3><p>{text}</p></article>
              ))}
            </div>
          </div>
        </section>

        <section className="section">
          <div className="shell parentGrid">
            <div className="parentCard parentDark">
              <span className="kicker kickerLight">Что получает ребёнок</span>
              <h2>Навык, а не набор фокусов</h2>
              <ul className="checkList">
                <li>умение объяснить задачу и разбить её на шаги;</li>
                <li>умение задавать AI понятный контекст;</li>
                <li>привычку проверять факты и сомневаться в ответе;</li>
                <li>собственный законченный проект;</li>
                <li>понимание правил приватности и авторства.</li>
              </ul>
            </div>
            <div className="parentCard">
              <span className="kicker">Что получает родитель</span>
              <h2>Понятный прогресс</h2>
              <ul className="checkList checkDark">
                <li>короткий стартовый план обучения;</li>
                <li>видимый результат после каждого блока;</li>
                <li>финальную работу, которую ребёнок презентует сам;</li>
                <li>рекомендации, как безопасно продолжать практику дома;</li>
                <li>никаких заявок или маркетинговых контактов напрямую ребёнку.</li>
              </ul>
            </div>
          </div>
        </section>

        <section className="section sectionMuted">
          <div className="shell">
            <div className="sectionHead splitHead"><div><span className="kicker">Формат и стоимость</span><h2>45–60 минут за занятие</h2></div><p>Индивидуально. Темп и сложность меняются под ребёнка, а не наоборот.</p></div>
            <div className="pricingGrid kidsPricing">
              <article className="priceCard"><span className="cardMeta">Mini</span><h3>4 занятия</h3><div className="price">$290</div><p>Первое знакомство с AI через творчество и небольшой мини-проект.</p><Link className="button buttonGhost buttonWide" href="/start">Выбрать Mini</Link></article>
              <article className="priceCard featuredPrice"><span className="popular">Основная программа</span><span className="cardMeta">Creator</span><h3>10 занятий</h3><div className="price">$890</div><p>Полный маршрут от основ до самостоятельной презентации итогового AI-проекта.</p><Link className="button buttonPrimary buttonWide" href="/start">Выбрать Creator</Link></article>
              <article className="priceCard"><span className="cardMeta">Studio</span><h3>12 занятий</h3><div className="price">$1,190</div><p>Больше времени на сложный проект, визуальную часть или первые технические эксперименты.</p><Link className="button buttonGhost buttonWide" href="/start">Выбрать Studio</Link></article>
            </div>
          </div>
        </section>

        <section className="section safetyBand">
          <div className="shell safetyBandGrid">
            <div><span className="kicker">Возраст и безопасность</span><h2>До 13 — взрослый остаётся в контуре.</h2></div>
            <div><p>Программа не требует самостоятельного аккаунта ChatGPT для ребёнка младше 13 лет. Если ChatGPT используется как демонстрационный инструмент, фактическое взаимодействие с сервисом проводит взрослый. Для любого AI-инструмента перед использованием проверяются его актуальные возрастные правила.</p><Link className="textLink" href="/safety">Все правила детской AI-безопасности <ArrowIcon /></Link></div>
          </div>
        </section>

        <section className="familyConciergeBand">
          <div className="shell familyConciergeGrid">
            <div><span className="kicker kickerLight">Family Concierge</span><h2>Для семьи, которой нужен более управляемый формат.</h2><p>12 занятий ребёнку + 2 отдельные сессии родителю + индивидуальный проект + правила безопасного использования AI дома.</p></div>
            <div className="familyConciergePrice"><span>PREMIUM</span><b>$1,490</b><Link className="button buttonLight buttonWide" href="/start">Обсудить Family</Link></div>
          </div>
        </section>

        <section className="section teenBridge">
          <div className="shell splitHead">
            <div><span className="kicker">Уже 14+</span><h2>Тогда нужен другой уровень.</h2></div>
            <div><p>Для подростков 14–18 программа смещается от творчества к исследованиям, портфолио, коду, автоматизациям и первым самостоятельным продуктам.</p><Link className="textLink" href="/teens">Открыть программу 14–18 <ArrowIcon /></Link></div>
          </div>
        </section>

        <section className="contactSection" id="kids-contact">
          <div className="shell contactGrid">
            <div><span className="kicker kickerLight">Для родителей</span><h2>Расскажите, чем ребёнок увлекается.</h2><p>Подберём тему первого проекта и объясним формат. Контактные данные в форме должны принадлежать взрослому.</p><ContactButtons fallbackHref="/start" /></div>
            <div className="contactOnlyCard"><span className="cardMeta">Для взрослого</span><h3>Короткий brief без данных ребёнка</h3><p>Возраст, интересы, цель и формат online / Phuket. Имя, телефон или email ребёнка на старте не нужны.</p><Link className="button buttonPrimary buttonWide" href="/start">Что написать →</Link></div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
