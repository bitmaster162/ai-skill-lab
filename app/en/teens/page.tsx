import type { Metadata } from "next";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = { title: "AI for teens ages 14–18", description: "AI for ages 14–18: research, code, portfolios and adult contact.", alternates: { canonical: "/en/teens", languages: { ru: "/teens", en: "/en/teens" } } };
export default function Page(){return <WorkshopAudience audience="teens" locale="en"/>;}
