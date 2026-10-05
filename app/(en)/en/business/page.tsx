import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { coursePageSchema } from "@/lib/structured-data";
import { WorkshopBusiness } from "@/components/workshop/WorkshopBusiness";
export const metadata: Metadata = {
  title: { absolute: "AI for business — AI Skill Lab · Phuket" },
  description: "Business AI at AI Skill Lab: workflow audit, team training, bounded pilots, QA and handoff from a defined process problem to a verifiable result.",
  alternates: { canonical: "/en/business", languages: { ru: "/business", en: "/en/business" } },
  twitter: { card: "summary_large_image", title: "AI for business", description: "Business AI at AI Skill Lab: workflow audit, team training, bounded pilots, QA and handoff from a defined process problem to a verifiable result.", images: ["/og.png"] },

  ...ogPageMetadata({ locale: "en", slug: "business", title: "AI for business — AI Skill Lab · Phuket", description: "Business AI at AI Skill Lab: workflow audit, team training, bounded pilots, QA and handoff from a defined process problem to a verifiable result." }),
};
export default function Page(){return <><JsonLd data={coursePageSchema("business", "en")} /><WorkshopBusiness locale="en"/></>;}
