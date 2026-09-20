import type { Metadata } from "next";
import { WorkshopBusiness } from "@/components/workshop/WorkshopBusiness";
export const metadata: Metadata = {
  title: { absolute: "AI для бизнеса — AI Skill Lab" },
  description: "AI для бизнеса: аудит, обучение, bounded pilot, QA и handoff.",
  alternates: { canonical: "/business", languages: { ru: "/business", en: "/en/business" } },
  twitter: { card: "summary_large_image", title: "AI для бизнеса", description: "AI для бизнеса: аудит, обучение, bounded pilot, QA и handoff.", images: ["/og.png"] },
};
export default function Page(){return <WorkshopBusiness locale="ru"/>;}
