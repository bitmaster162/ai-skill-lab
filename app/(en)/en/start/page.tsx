import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { WorkshopStart } from "@/components/workshop/WorkshopStart";
export const metadata: Metadata = { title: { absolute: "Start — pick a track and a first task | AI Skill Lab · Phuket" }, description: "Choose a request type, compile a short brief, and contact AI Skill Lab by Telegram, email, WhatsApp or LINE under clear privacy and adult-contact rules.", alternates: { canonical: "/en/start", languages: { ru: "/start", en: "/en/start" } } ,
  ...ogPageMetadata({ locale: "en", slug: "start", title: "Start — pick a track and a first task | AI Skill Lab · Phuket", description: "Choose a request type, compile a short brief, and contact AI Skill Lab by Telegram, email, WhatsApp or LINE under clear privacy and adult-contact rules." }),
};
export default function StartPage(){return <WorkshopStart locale="en"/>}
