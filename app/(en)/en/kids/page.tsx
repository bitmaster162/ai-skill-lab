import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { coursePageSchema } from "@/lib/structured-data";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = { title: { absolute: "AI for kids 8–13 — AI Skill Lab · Phuket" }, description: "AI for ages 8–13: creative work and a personal project with adult guidance, privacy rules, verification habits and age-appropriate AI practice.", alternates: { canonical: "/en/kids", languages: { ru: "/kids", en: "/en/kids" } } ,
  ...ogPageMetadata({ locale: "en", slug: "kids", title: "AI for kids 8–13 — AI Skill Lab · Phuket", description: "AI for ages 8–13: creative work and a personal project with adult guidance, privacy rules, verification habits and age-appropriate AI practice." }),
};
export default function Page(){return <><JsonLd data={coursePageSchema("kids", "en")} /><WorkshopAudience audience="kids" locale="en"/></>;}
