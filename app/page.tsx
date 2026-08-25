import type { Metadata } from "next";
import { JsonLd } from "@/components/JsonLd";
import { organizationSchemaRu, websiteSchema } from "@/lib/structured-data";
import { R77CommercialHome } from "@/components/R77CommercialHome";

export const metadata: Metadata = {
  title: "AI Skill Lab — персональное обучение и AI workflow pilot",
  description: "Практическое обучение AI 1-на-1, AI Studio и один проверяемый workflow-pilot для бизнеса — online worldwide и Phuket.",
  alternates: { canonical: "/", languages: { ru: "/", en: "/en" } },
};

export default function Home() {
  return (
    <>
      <JsonLd data={[websiteSchema, organizationSchemaRu]} />
      <R77CommercialHome locale="ru" />
    </>
  );
}
