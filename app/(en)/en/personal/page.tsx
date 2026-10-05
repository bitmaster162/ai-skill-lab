import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { coursePageSchema } from "@/lib/structured-data";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = { title: { absolute: "Personal AI training — AI Skill Lab · Phuket" }, description: "One-to-one AI sessions built around a real task: hands-on practice, a verifiable project, tool selection and work online or by arrangement in Phuket.", alternates: { canonical: "/en/personal", languages: { ru: "/personal", en: "/en/personal" } } ,
  ...ogPageMetadata({ locale: "en", slug: "personal", title: "Personal AI training — AI Skill Lab · Phuket", description: "One-to-one AI sessions built around a real task: hands-on practice, a verifiable project, tool selection and work online or by arrangement in Phuket." }),
};
export default function Page(){return <><JsonLd data={coursePageSchema("personal", "en")} /><WorkshopAudience audience="adult" locale="en"/></>;}
