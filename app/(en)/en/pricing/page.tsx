import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { courseListSchema } from "@/lib/structured-data";
import { WorkshopPricing } from "@/components/workshop/WorkshopPricing";
export const metadata: Metadata = { title: { absolute: "Pricing and formats — AI Skill Lab · Phuket" }, description: "Transparent AI Skill Lab pricing: 60-minute sessions, personal packages, business pilots and bounded recurring support.", alternates: { canonical: "/en/pricing", languages: { ru: "/pricing", en: "/en/pricing" } } ,
  ...ogPageMetadata({ locale: "en", slug: "pricing", title: "Pricing and formats — AI Skill Lab · Phuket", description: "Transparent AI Skill Lab pricing: 60-minute sessions, personal packages, business pilots and bounded recurring support." }),
};
export default function PricingPage(){return <><JsonLd data={courseListSchema("en")} /><WorkshopPricing locale="en"/></>}
