import type { Metadata } from "next";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = {
  title: "AI для подростков 14–18 лет",
  description: "AI 14–18: research, код, портфолио и контакт через взрослого.",
  alternates: { canonical: "/teens", languages: { ru: "/teens", en: "/en/teens" } },
};
export default function Page(){return <WorkshopAudience audience="teens" locale="ru"/>;}
