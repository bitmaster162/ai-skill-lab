import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { WorkshopHome } from "@/components/workshop/WorkshopHome";
import { websiteSchema } from "@/lib/structured-data";

export const metadata: Metadata = { title: { absolute: "AI Skill Lab · Phuket — персональное обучение и AI workflow pilot" }, description: "Практическое обучение AI 1-на-1, AI Studio и один проверяемый workflow-pilot для бизнеса — online worldwide и Phuket.", alternates: { canonical: "/", languages: { ru: "/", en: "/en" } } ,
  ...ogPageMetadata({ locale: "ru", slug: "home", title: "AI Skill Lab · Phuket — персональное обучение и AI workflow pilot", description: "Практическое обучение AI 1-на-1, AI Studio и один проверяемый workflow-pilot для бизнеса — online worldwide и Phuket." }),
};
export default function Home(){return <><JsonLd data={websiteSchema} /><WorkshopHome locale="ru" /></>}
