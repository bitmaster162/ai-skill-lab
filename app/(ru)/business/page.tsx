import type { Metadata } from "next";
import { JsonLd } from "@/components/JsonLd";
import { coursePageSchema } from "@/lib/structured-data";
import { WorkshopBusiness } from "@/components/workshop/WorkshopBusiness";
export const metadata: Metadata = {
  title: { absolute: "AI для бизнеса — AI Skill Lab · Phuket" },
  description: "AI для бизнеса: аудит процессов, обучение команды, bounded pilot, QA и handoff — от выбора задачи до проверяемого результата без лишних обещаний.",
  alternates: { canonical: "/business", languages: { ru: "/business", en: "/en/business" } },
  twitter: { card: "summary_large_image", title: "AI для бизнеса", description: "AI для бизнеса: аудит процессов, обучение команды, bounded pilot, QA и handoff — от выбора задачи до проверяемого результата без лишних обещаний.", images: ["/og.png"] },
};
export default function Page(){return <><JsonLd data={coursePageSchema("business", "ru")} /><WorkshopBusiness locale="ru"/></>;}
