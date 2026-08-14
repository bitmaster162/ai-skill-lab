import type { Metadata } from "next";
import Link from "next/link";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "Стоимость обучения AI",
  description: "Прозрачные пакеты AI Skill Lab для взрослых, детей, подростков и семей. Без checkout: формат подтверждается до оплаты.",
  alternates: { canonical: "/pricing", languages: { ru: "/pricing", en: "/en/pricing" } },
};

const groups = [
  ["Взрослым", [["Start", "$390", "4 занятия", "Быстрый вход и первый рабочий AI-процесс."], ["Personal", "$890", "10 занятий", "Основная персональная траектория с итоговым проектом."], ["Intensive", "$1,290", "12 занятий + проект", "Для automation, agent или технического mini-product."]]],
  ["Дети 8–13", [["Mini", "$290", "4 занятия", "Знакомство и небольшой проект."], ["Creator", "$890", "10 занятий", "Полная программа с самостоятельной презентацией."], ["Studio", "$1,190", "12 занятий", "Больше времени на сложный проект."]]],
  ["Подростки 14–18", [["Explorer", "$490", "6 занятий", "AI literacy, research и небольшой проект."], ["Portfolio", "$890", "10 занятий", "Полный маршрут с законченной работой."], ["Builder", "$1,290", "12 занятий", "Больше кода, automation и product thinking."]]],
];

export default function PricingPage() {
  return <><Header contactHref="/start" alternateHref="/en/pricing"/><main id="main"><section className="hero heroR2"><div className="shell"><div className="eyebrow"><span className="dot"/> PRICING · 1:1</div><h1>Цена понятна<br/><span>до старта.</span></h1><p className="heroLead">На сайте нет checkout. Сначала фиксируем цель, формат и состав программы, затем подтверждаем оплату и правила переноса.</p><div className="heroActions"><Link className="button buttonPrimary" href="/start">Подобрать пакет →</Link><Link className="textLink" href="/method">Как устроено обучение →</Link></div></div></section>{groups.map(([name, items])=><section className="section" key={name as string}><div className="shell"><div className="sectionHead"><span className="kicker">{name as string}</span></div><div className="pricingGrid">{(items as string[][]).map(([plan,price,length,text],i)=><article className={`priceCard ${i===1?"featuredPrice":""}`} key={plan}>{i===1&&<span className="popular">Основной</span>}<span className="cardMeta">{plan}</span><h3>{length}</h3><div className="price">{price}</div><p>{text}</p></article>)}</div></div></section>)}<section className="section sectionMuted"><div className="shell premiumParentGrid"><div><span className="kicker">Family Concierge</span><h2>12 занятий + 2 сессии родителю</h2><p>Индивидуальный маршрут, семейные правила использования AI, итоговый проект и отдельный взрослый контур.</p></div><article className="premiumPriceCard"><div className="price">$1,490</div><Link className="button buttonPrimary buttonWide" href="/start">Обсудить Family</Link></article></div></section></main><Footer/></>;
}
