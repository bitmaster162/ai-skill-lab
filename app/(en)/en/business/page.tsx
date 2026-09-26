import type { Metadata } from "next";
import { WorkshopBusiness } from "@/components/workshop/WorkshopBusiness";
export const metadata: Metadata = {
  title: { absolute: "AI for business — AI Skill Lab" },
  description: "Business AI at AI Skill Lab: workflow audit, team training, bounded pilots, QA and handoff from a defined process problem to a verifiable result.",
  alternates: { canonical: "/en/business", languages: { ru: "/business", en: "/en/business" } },
  twitter: { card: "summary_large_image", title: "AI for business", description: "Business AI at AI Skill Lab: workflow audit, team training, bounded pilots, QA and handoff from a defined process problem to a verifiable result.", images: ["/og.png"] },
};
export default function Page(){return <WorkshopBusiness locale="en"/>;}
