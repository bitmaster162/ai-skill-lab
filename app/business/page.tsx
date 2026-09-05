import type { Metadata } from "next";
import { WorkshopBusiness } from "@/components/workshop/WorkshopBusiness";
export const metadata: Metadata = {
  title: "AI для бизнеса",
  description: "AI для бизнеса: аудит, обучение, bounded pilot, QA и handoff.",
  alternates: { canonical: "/business", languages: { ru: "/business", en: "/en/business" } },
  twitter: { card: "summary_large_image", title: "AI для бизнеса", description: "AI для бизнеса: аудит, обучение, bounded pilot, QA и handoff.", images: ["/opengraph-image"] },
};
export default function Page(){return <WorkshopBusiness locale="ru"/>;}
