import type { Metadata } from "next";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = { title: { absolute: "Personal AI training — AI Skill Lab" }, description: "One-to-one AI sessions built around a real task: hands-on practice, a verifiable project, tool selection and work online or by arrangement in Phuket.", alternates: { canonical: "/en/personal", languages: { ru: "/personal", en: "/en/personal" } } };
export default function Page(){return <WorkshopAudience audience="adult" locale="en"/>;}
