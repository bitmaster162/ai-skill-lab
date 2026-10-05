import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { coursePageSchema } from "@/lib/structured-data";
import { WorkshopAudience } from "@/components/workshop/WorkshopAudience";
export const metadata: Metadata = {
  title: { absolute: "AI для детей 8–13 — AI Skill Lab · Phuket" },
  description: "AI для детей 8–13: творчество и собственный проект с участием взрослого, правилами приватности, проверкой результата и безопасной практикой.",
  alternates: { canonical: "/kids", languages: { ru: "/kids", en: "/en/kids" } },

  ...ogPageMetadata({ locale: "ru", slug: "kids", title: "AI для детей 8–13 — AI Skill Lab · Phuket", description: "AI для детей 8–13: творчество и собственный проект с участием взрослого, правилами приватности, проверкой результата и безопасной практикой." }),
};
export default function Page(){return <><JsonLd data={coursePageSchema("kids", "ru")} /><WorkshopAudience audience="kids" locale="ru"/></>;}
