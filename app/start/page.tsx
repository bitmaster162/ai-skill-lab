import type { Metadata } from "next";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { site } from "@/lib/site";
export const metadata: Metadata = { title: "Начать обучение", alternates: { canonical: "/start", languages: { ru: "/start", en: "/en/start" } } };
export default function StartPage(){return <><Header contactHref={site.telegram}/><main id="main"><section className="contactSection"><div className="shell contactGrid"><div><span className="kicker kickerLight">START · без формы</span><h2>Сначала fit.<br/>Потом программа.</h2><p>Коротко опишите: кому обучение, цель, текущий уровень и формат online / Phuket. Для несовершеннолетнего контакт ведёт взрослый.</p><div className="contactButtons"><a className="button buttonLight" href={site.telegram} target="_blank" rel="noopener noreferrer">Открыть Telegram →</a></div></div><div className="contactOnlyCard"><h3>Что написать</h3><p>1. Кому обучение<br/>2. Что должно стать возможным<br/>3. Текущий уровень<br/>4. Online / Phuket и RU / EN</p><small>Не присылайте лишние персональные данные ребёнка.</small></div></div></section></main><Footer/></>;}
