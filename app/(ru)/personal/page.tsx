import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { coursePageSchema } from "@/lib/structured-data";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = {
  title: { absolute: "Персональное обучение ИИ 1-на-1 — AI Skill Lab · Пхукет" },
  description: "Занятия по ИИ и нейросетям 1-на-1 вокруг вашей реальной задачи: практика, свой проект и разбор инструментов. На Пхукете или онлайн.",
  alternates: { canonical: "/personal", languages: { ru: "/personal", en: "/en/personal" } },

  ...ogPageMetadata({ locale: "ru", slug: "personal", title: "Персональное обучение ИИ 1-на-1 — AI Skill Lab · Пхукет", description: "Занятия по ИИ и нейросетям 1-на-1 вокруг вашей реальной задачи: практика, свой проект и разбор инструментов. На Пхукете или онлайн." }),
};
export default function Page(){return <><JsonLd data={coursePageSchema("personal", "ru")} /><WorkshopAudience audience="adult" locale="ru"/></>;}
