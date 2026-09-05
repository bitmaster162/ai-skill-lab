import type { Metadata } from "next";
import { WorkshopStart } from "@/components/workshop/WorkshopStart";
export const metadata: Metadata = { title: "Начать обучение", description: "Выберите тип запроса, скопируйте короткий brief и свяжитесь через Telegram, почту, WhatsApp или LINE.", alternates: { canonical: "/start", languages: { ru: "/start", en: "/en/start" } } };
export default function StartPage(){return <WorkshopStart locale="ru"/>}
