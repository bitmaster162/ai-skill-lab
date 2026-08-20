import type { Metadata } from "next";
import { JsonLd } from "@/components/JsonLd";
import { organizationSchemaEn, websiteSchema } from "@/lib/structured-data";
import { R70BroadsheetHome } from "@/components/R70BroadsheetHome";

export const metadata: Metadata = {
  title: "Personal AI education",
  description: "Practical one-to-one AI education for adults, kids, teens and teams: real projects, research, automation and responsible AI use.",
  alternates: { canonical: "/en", languages: { ru: "/", en: "/en" } },
};

export default function EnglishHome() {
  return (
    <>
      <JsonLd data={[websiteSchema, organizationSchemaEn]} />
      <R70BroadsheetHome locale="en" />
    </>
  );
}
