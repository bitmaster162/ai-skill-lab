import type { Metadata } from "next";
import { WorkshopStart } from "@/components/workshop/WorkshopStart";
export const metadata: Metadata = { title: "Start", description: "Choose a request type, copy a short brief and contact AI Skill Lab by Telegram, email, WhatsApp or LINE.", alternates: { canonical: "/en/start", languages: { ru: "/start", en: "/en/start" } } };
export default function StartPage(){return <WorkshopStart locale="en"/>}
