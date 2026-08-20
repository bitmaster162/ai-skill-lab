import type { Metadata } from "next";
import { JsonLd } from "@/components/JsonLd";
import { organizationSchemaRu, websiteSchema } from "@/lib/structured-data";
import { R70BroadsheetHome } from "@/components/R70BroadsheetHome";

export const metadata: Metadata = {
  alternates: { canonical: "/", languages: { ru: "/", en: "/en" } },
};

export default function Home() {
  return (
    <>
      <JsonLd data={[websiteSchema, organizationSchemaRu]} />
      <R70BroadsheetHome locale="ru" />
    </>
  );
}
