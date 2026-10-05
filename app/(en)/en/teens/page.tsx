import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { coursePageSchema } from "@/lib/structured-data";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = { title: { absolute: "AI for teens 14–18 — AI Skill Lab · Phuket" }, description: "AI for ages 14–18: research, code, portfolios and independent projects with verification, authorship rules, practical AI work and adult contact.", alternates: { canonical: "/en/teens", languages: { ru: "/teens", en: "/en/teens" } } ,
  ...ogPageMetadata({ locale: "en", slug: "teens", title: "AI for teens 14–18 — AI Skill Lab · Phuket", description: "AI for ages 14–18: research, code, portfolios and independent projects with verification, authorship rules, practical AI work and adult contact." }),
};
export default function Page(){return <><JsonLd data={coursePageSchema("teens", "en")} /><WorkshopAudience audience="teens" locale="en"/></>;}
