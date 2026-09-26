import type { Metadata } from "next";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = { title: { absolute: "AI for kids 8–13 — AI Skill Lab" }, description: "AI for ages 8–13: creative work and a personal project with adult guidance, privacy rules, verification habits and age-appropriate AI practice.", alternates: { canonical: "/en/kids", languages: { ru: "/kids", en: "/en/kids" } } };
export default function Page(){return <WorkshopAudience audience="kids" locale="en"/>;}
