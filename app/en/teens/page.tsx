import type { Metadata } from "next";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = { title: { absolute: "AI for teens 14–18 — AI Skill Lab" }, description: "AI for ages 14–18: research, code, portfolios and adult contact.", alternates: { canonical: "/en/teens", languages: { ru: "/teens", en: "/en/teens" } } };
export default function Page(){return <WorkshopAudience audience="teens" locale="en"/>;}
