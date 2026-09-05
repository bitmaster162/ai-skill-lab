import type { Metadata } from "next";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = { title: "Personal AI training", description: "One-to-one AI: real tasks and verifiable projects, online / Phuket.", alternates: { canonical: "/en/personal", languages: { ru: "/personal", en: "/en/personal" } } };
export default function Page(){return <WorkshopAudience audience="adult" locale="en"/>;}
