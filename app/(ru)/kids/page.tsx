import type { Metadata } from "next";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = {
  title: { absolute: "AI для детей 8–13 — AI Skill Lab" },
  description: "AI для детей 8–13: творчество и собственный проект с участием взрослого, правилами приватности, проверкой результата и безопасной практикой.",
  alternates: { canonical: "/kids", languages: { ru: "/kids", en: "/en/kids" } },
};
export default function Page(){return <WorkshopAudience audience="kids" locale="ru"/>;}
