import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { WorkshopHome } from "@/components/workshop/WorkshopHome";
import { websiteSchema } from "@/lib/structured-data";

export const metadata: Metadata = { title: { absolute: "Обучение ИИ 1-на-1 на Пхукете и онлайн — AI Skill Lab" }, description: "Персональные занятия по ИИ и нейросетям для взрослых, подростков, детей и команд. Пхукет и онлайн, на русском и английском. Бесплатный звонок 15 минут.", alternates: { canonical: "/", languages: { ru: "/", en: "/en" } } ,
  ...ogPageMetadata({ locale: "ru", slug: "home", title: "Обучение ИИ 1-на-1 на Пхукете и онлайн — AI Skill Lab", description: "Персональные занятия по ИИ и нейросетям для взрослых, подростков, детей и команд. Пхукет и онлайн, на русском и английском. Бесплатный звонок 15 минут." }),
};
export default function Home(){return <><JsonLd data={websiteSchema} /><WorkshopHome locale="ru" /></>}
