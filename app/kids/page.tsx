import type { Metadata } from "next";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = {
  title: "AI для детей 8–13 лет",
  description: "AI 8–13: творчество, свой проект, приватность и участие взрослого.",
  alternates: { canonical: "/kids", languages: { ru: "/kids", en: "/en/kids" } },
};
export default function Page(){return <WorkshopAudience audience="kids" locale="ru"/>;}
