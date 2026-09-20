import type { Metadata } from "next";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = {
  title: { absolute: "Персональное обучение AI — AI Skill Lab" },
  description: "AI 1-на-1: реальная задача, проверяемый проект, online / Phuket.",
  alternates: { canonical: "/personal", languages: { ru: "/personal", en: "/en/personal" } },
};
export default function Page(){return <WorkshopAudience audience="adult" locale="ru"/>;}
