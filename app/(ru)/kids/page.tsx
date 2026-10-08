import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { coursePageSchema } from "@/lib/structured-data";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = {
  title: { absolute: "ИИ для детей 8–13 лет на Пхукете и онлайн — AI Skill Lab" },
  description: "Занятия по ИИ и нейросетям для детей 8–13 лет: свой творческий проект вместе со взрослым, правила приватности и безопасная практика. Пхукет и онлайн.",
  alternates: { canonical: "/kids", languages: { ru: "/kids", en: "/en/kids" } },

  ...ogPageMetadata({ locale: "ru", slug: "kids", title: "ИИ для детей 8–13 лет на Пхукете и онлайн — AI Skill Lab", description: "Занятия по ИИ и нейросетям для детей 8–13 лет: свой творческий проект вместе со взрослым, правила приватности и безопасная практика. Пхукет и онлайн." }),
};
export default function Page(){return <><JsonLd data={coursePageSchema("kids", "ru")} /><WorkshopAudience audience="kids" locale="ru"/></>;}
