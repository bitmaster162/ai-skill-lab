import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { WorkshopHome } from "@/components/workshop/WorkshopHome";
import { websiteSchema } from "@/lib/structured-data";

export const metadata: Metadata = { title: { absolute: "AI Skill Lab · Phuket — practical AI learning and workflow pilots" }, description: "One-to-one practical AI learning, AI Studio and one verifiable workflow pilot for business — online worldwide and in Phuket.", alternates: { canonical: "/en", languages: { ru: "/", en: "/en" } } ,
  ...ogPageMetadata({ locale: "en", slug: "home", title: "AI Skill Lab · Phuket — practical AI learning and workflow pilots", description: "One-to-one practical AI learning, AI Studio and one verifiable workflow pilot for business — online worldwide and in Phuket." }),
};
export default function EnglishHome(){return <><JsonLd data={websiteSchema} /><WorkshopHome locale="en" /></>}
