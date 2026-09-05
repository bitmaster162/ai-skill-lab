import type { Metadata } from "next";
import { WorkshopFamily } from "@/components/workshop/WorkshopFamily";
export const metadata: Metadata = { title: "Family Concierge — семейная AI-программа", description: "Family Concierge: 12 персональных занятий с учеником, 2 сессии с родителем, итоговый проект и семейные правила безопасного использования AI.", alternates: { canonical: "/family", languages: { ru: "/family", en: "/en/family" } } };
export default function FamilyPage(){return <WorkshopFamily locale="ru"/>}
