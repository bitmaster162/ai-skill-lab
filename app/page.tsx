import type { Metadata } from "next";
import { JsonLd } from "@/components/JsonLd";
import { WorkshopHome } from "@/components/workshop/WorkshopHome";
import { organizationSchemaRu, websiteSchema } from "@/lib/structured-data";

export const metadata: Metadata = { title: "AI Skill Lab — персональное обучение и AI workflow pilot", description: "Практическое обучение AI 1-на-1, AI Studio и один проверяемый workflow-pilot для бизнеса — online worldwide и Phuket.", alternates: { canonical: "/", languages: { ru: "/", en: "/en" } } };
export default function Home(){return <><JsonLd data={[websiteSchema, organizationSchemaRu]} /><WorkshopHome locale="ru" /></>}
