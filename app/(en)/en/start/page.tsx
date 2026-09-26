import type { Metadata } from "next";
import { WorkshopStart } from "@/components/workshop/WorkshopStart";
export const metadata: Metadata = { title: "Start — pick a track and a first task", description: "Choose a request type, compile a short brief, and contact AI Skill Lab by Telegram, email, WhatsApp or LINE under clear privacy and adult-contact rules.", alternates: { canonical: "/en/start", languages: { ru: "/start", en: "/en/start" } } };
export default function StartPage(){return <WorkshopStart locale="en"/>}
