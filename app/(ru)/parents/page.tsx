import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { WorkshopEditorial } from "@/components/workshop/WorkshopEditorial";
import Link from "next/link";
import { IntroCallCta } from "@/components/IntroCallCta";
export const metadata: Metadata = {
  title: { absolute: "Родителям: обучение ИИ — AI Skill Lab · Пхукет" },
  description: "Что получает родитель в AI-программе 8–18: видимый прогресс, проект, правила безопасности и прозрачная роль взрослого.",
  alternates: { canonical: "/parents", languages: { ru: "/parents", en: "/en/parents" } },

  ...ogPageMetadata({ locale: "ru", slug: "parents", title: "Родителям: обучение ИИ — AI Skill Lab · Пхукет", description: "Что получает родитель в AI-программе 8–18: видимый прогресс, проект, правила безопасности и прозрачная роль взрослого." }),
};

export default function Page() {
  return <WorkshopEditorial locale="ru" alternateHref="/en/parents">
    <main id="main">
      <section className="kidsHero"><div className="shell kidsHeroGrid"><div>
        <div className="eyebrow eyebrowLight"><span className="dot dotLight" /> РОДИТЕЛЯМ · 8–18</div>
        <h1>Не «ИИ сделал».<br/><span>Ребёнок умеет.</span></h1>
        <p>Прогресс в обучении ИИ виден через способность поставить задачу, проверить ответ, объяснить личный вклад и защитить финальный проект.</p>
        <IntroCallCta locale="ru"/>
        <div className="heroActions"><Link className="button buttonLight" href="/start">Обсудить маршрут →</Link><Link className="button buttonGhost buttonOnDark" href="/projects">Примеры проектов →</Link></div>
      </div></div></section>

      <section className="section"><div className="shell">
        <div className="sectionHead"><span className="kicker">КРИТЕРИИ ПРОГРЕССА</span><h2>Навык должен быть виден.</h2></div>
        <div className="kidsPrinciples">
          <article><span>01</span><h3>Сам формулирует цель</h3><p>Ученик может объяснить, что именно он хочет получить и зачем.</p></article>
          <article><span>02</span><h3>Проверяет утверждения</h3><p>Ответ ИИ не считается фактом только потому, что звучит уверенно.</p></article>
          <article><span>03</span><h3>Объясняет, что сделал сам</h3><p>Личный вклад и помощь ИИ разделяются прозрачно.</p></article>
          <article><span>04</span><h3>Защищает финальный проект</h3><p>Результат нужно уметь показать, объяснить и улучшить.</p></article>
        </div>
      </div></section>

      <section className="section sectionMuted"><div className="shell">
        <div className="sectionHead"><span className="kicker">Что покупает семья</span><h2>Не просто инструмент. Система обучения.</h2></div>
        <div className="pricingGrid">
          <article className="priceCard"><span className="cardMeta">МАРШРУТ</span><h3>Персональный маршрут</h3><p>Темы и проект выбираются вокруг интересов ученика, а не одинакового списка промптов.</p></article>
          <article className="priceCard"><span className="cardMeta">ВИДИМЫЙ ПРОГРЕСС</span><h3>Проверяемый результат</h3><p>После занятий остаются артефакты и финальный проект, который ученик должен уметь объяснить.</p></article>
          <article className="priceCard"><span className="cardMeta">ЗАНЯТИЯ ДЛЯ РОДИТЕЛЕЙ</span><h3>Взрослый в контуре</h3><p>Организация, возрастные ограничения и выбор сервисов обсуждаются со взрослым.</p></article>
        </div>
      </div></section>

      <section className="section"><div className="shell"><div className="sectionHead">
        <span className="kicker">Возрастные правила</span><h2>ChatGPT и возраст.</h2>
        <p>ChatGPT не предназначен для детей младше 13 лет. Для пользователей 13–18 требуется согласие родителя или законного представителя. В образовательном контексте с ребёнком младше 13 непосредственное взаимодействие с ChatGPT проводит взрослый.</p>
        <div className="heroActions"><a className="textLink" href="https://help.openai.com/en/articles/8313401" target="_blank" rel="noopener noreferrer">Официальная справка OpenAI →</a><Link className="textLink" href="/safety">Наш подход к безопасности →</Link><Link className="textLink" href="/guides/ai-safety-for-kids">Чек-лист для родителей: возраст, данные, родительский контроль →</Link></div>
      </div></div></section>

      <section className="section sectionMuted"><div className="shell">
        <div className="sectionHead"><span className="kicker">Форматы 8–13</span><h2>Три уровня глубины.</h2></div>
        <div className="pricingGrid">
          <article className="priceCard"><span className="cardMeta">Mini</span><h3>4 занятия</h3><div className="price">$290</div><p>Знакомство с подходом и небольшой проект.</p></article>
          <article className="priceCard featuredPrice"><span className="cardMeta">Creator</span><h3>10 занятий</h3><div className="price">$890</div><p>Основная программа и самостоятельная презентация проекта.</p></article>
          <article className="priceCard"><span className="cardMeta">Studio</span><h3>12 занятий</h3><div className="price">$1,190</div><p>Больше времени на сложный, визуальный или технический проект.</p></article>
        </div>
      </div></section>

      <section className="section"><div className="shell">
        <div className="sectionHead"><span className="kicker">Форматы 14–18</span><h2>От ИИ-грамотности к портфолио.</h2></div>
        <div className="pricingGrid">
          <article className="priceCard"><span className="cardMeta">Explorer</span><h3>6 занятий</h3><div className="price">$490</div><p>ИИ-грамотность, исследование и небольшой проект.</p></article>
          <article className="priceCard featuredPrice"><span className="cardMeta">Portfolio</span><h3>10 занятий</h3><div className="price">$890</div><p>Полный маршрут с законченной работой.</p></article>
          <article className="priceCard"><span className="cardMeta">Builder</span><h3>12 занятий</h3><div className="price">$1,290</div><p>Больше кода, автоматизация и продуктовое мышление.</p></article>
        </div>
      </div></section>

      <section className="section sectionMuted"><div className="shell premiumParentGrid"><div>
        <span className="kicker">Family Concierge</span><h2>12 занятий + 2 сессии родителю</h2>
        <p>Расширенный маршрут, отдельный цикл занятий для родителя, итоговый проект и семейные правила использования ИИ.</p>
      </div><article className="premiumPriceCard"><div className="price">$1,490</div><Link className="button buttonPrimary buttonWide" href="/start">Обсудить Семья</Link></article></div></section>

      <section className="section"><div className="shell"><div className="sectionHead">
        <span className="kicker">Первое короткое описание задачи</span><h2>Возраст + интерес + цель — достаточно.</h2>
        <p>Не нужно заранее выбирать инструменты и не нужно присылать лишние персональные данные ребёнка.</p>
        <Link className="button buttonPrimary" href="/start">Как начать →</Link>
      </div></div></section>
    </main>
    </WorkshopEditorial>;
}
