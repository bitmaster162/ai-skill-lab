import type { Metadata } from "next";
import { WorkshopPricing } from "@/components/workshop/WorkshopPricing";
export const metadata: Metadata = { title: "Pricing and formats", description: "Transparent AI Skill Lab pricing: 60-minute sessions, personal packages, business pilots and bounded recurring support.", alternates: { canonical: "/en/pricing", languages: { ru: "/pricing", en: "/en/pricing" } } };
export default function PricingPage(){return <WorkshopPricing locale="en"/>}
