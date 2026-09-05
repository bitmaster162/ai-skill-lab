import type { Metadata } from "next";
import { WorkshopFamily } from "@/components/workshop/WorkshopFamily";
export const metadata: Metadata = { title: "Family Concierge — family AI program", description: "Family Concierge: 12 learner sessions, 2 parent sessions, a final project and written household rules for safer, more independent AI use.", alternates: { canonical: "/en/family", languages: { ru: "/family", en: "/en/family" } } };
export default function FamilyPage(){return <WorkshopFamily locale="en"/>}
