import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { coursePageSchema } from "@/lib/structured-data";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = {
  title: { absolute: "ИИ для подростков 14–18 на Пхукете и онлайн — AI Skill Lab" },
  description: "Подростки 14–18 лет работают с ИИ и нейросетями: исследования, код, портфолио и свои проекты с проверкой результата. Пхукет и онлайн.",
  alternates: { canonical: "/teens", languages: { ru: "/teens", en: "/en/teens" } },

  ...ogPageMetadata({ locale: "ru", slug: "teens", title: "ИИ для подростков 14–18 на Пхукете и онлайн — AI Skill Lab", description: "Подростки 14–18 лет работают с ИИ и нейросетями: исследования, код, портфолио и свои проекты с проверкой результата. Пхукет и онлайн." }),
};
export default function Page(){return <><JsonLd data={coursePageSchema("teens", "ru")} /><WorkshopAudience audience="teens" locale="ru"/></>;}
