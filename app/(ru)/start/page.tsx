import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { WorkshopStart } from "@/components/workshop/WorkshopStart";
export const metadata: Metadata = { title: { absolute: "Записаться на обучение ИИ — AI Skill Lab" }, description: "Оставьте короткую заявку или напишите в Telegram, WhatsApp, LINE или на почту. Бесплатный звонок 15 минут, ответ в течение 1–2 рабочих дней.", alternates: { canonical: "/start", languages: { ru: "/start", en: "/en/start" } } ,
  ...ogPageMetadata({ locale: "ru", slug: "start", title: "Записаться на обучение ИИ — AI Skill Lab", description: "Оставьте короткую заявку или напишите в Telegram, WhatsApp, LINE или на почту. Бесплатный звонок 15 минут, ответ в течение 1–2 рабочих дней." }),
};
export default function StartPage(){return <WorkshopStart locale="ru"/>}
