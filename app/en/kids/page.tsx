import type { Metadata } from "next";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = { title: "AI for kids ages 8–13", description: "AI for ages 8–13: creativity, projects, privacy and adult guidance.", alternates: { canonical: "/en/kids", languages: { ru: "/kids", en: "/en/kids" } } };
export default function Page(){return <WorkshopAudience audience="kids" locale="en"/>;}
