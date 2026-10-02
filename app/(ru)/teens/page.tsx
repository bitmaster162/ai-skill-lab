import type { Metadata } from "next";
import { JsonLd } from "@/components/JsonLd";
import { coursePageSchema } from "@/lib/structured-data";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = {
  title: { absolute: "AI для подростков 14–18 — AI Skill Lab · Phuket" },
  description: "AI для подростков 14–18: research, код, портфолио и собственные проекты с проверкой результата, правилами авторства и контактом через взрослого.",
  alternates: { canonical: "/teens", languages: { ru: "/teens", en: "/en/teens" } },
};
export default function Page(){return <><JsonLd data={coursePageSchema("teens", "ru")} /><WorkshopAudience audience="teens" locale="ru"/></>;}
