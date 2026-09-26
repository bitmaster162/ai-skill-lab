import type { Metadata } from "next";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = {
  title: { absolute: "Персональное обучение AI — AI Skill Lab" },
  description: "Персональные занятия AI 1-на-1 вокруг реальной задачи: практика, проверяемый проект, разбор инструментов и работа online или на Phuket.",
  alternates: { canonical: "/personal", languages: { ru: "/personal", en: "/en/personal" } },
};
export default function Page(){return <WorkshopAudience audience="adult" locale="ru"/>;}
