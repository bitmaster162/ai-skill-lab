import type { Metadata } from "next";
import { JsonLd } from "@/components/JsonLd";
import { WorkshopHome } from "@/components/workshop/WorkshopHome";
import { organizationSchemaEn, websiteSchema } from "@/lib/structured-data";

export const metadata: Metadata = { title: "AI Skill Lab — practical AI learning and workflow pilots", description: "One-to-one practical AI learning, AI Studio and one verifiable workflow pilot for business — online worldwide and in Phuket.", alternates: { canonical: "/en", languages: { ru: "/", en: "/en" } } };
export default function EnglishHome(){return <><JsonLd data={[websiteSchema, organizationSchemaEn]} /><WorkshopHome locale="en" /></>}
