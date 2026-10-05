import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { coursePageSchema } from "@/lib/structured-data";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = {
  title: { absolute: "Персональное обучение AI — AI Skill Lab · Phuket" },
  description: "Персональные занятия AI 1-на-1 вокруг реальной задачи: практика, проверяемый проект, разбор инструментов и работа online или на Phuket.",
  alternates: { canonical: "/personal", languages: { ru: "/personal", en: "/en/personal" } },

  ...ogPageMetadata({ locale: "ru", slug: "personal", title: "Персональное обучение AI — AI Skill Lab · Phuket", description: "Персональные занятия AI 1-на-1 вокруг реальной задачи: практика, проверяемый проект, разбор инструментов и работа online или на Phuket." }),
};
export default function Page(){return <><JsonLd data={coursePageSchema("personal", "ru")} /><WorkshopAudience audience="adult" locale="ru"/></>;}
