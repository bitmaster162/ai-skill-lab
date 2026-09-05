import type { Metadata } from "next";
import { WorkshopBusiness } from "@/components/workshop/WorkshopBusiness";
export const metadata: Metadata = {
  title: "AI for business",
  description: "Business AI: workflow audit, team training, bounded pilots and QA.",
  alternates: { canonical: "/en/business", languages: { ru: "/business", en: "/en/business" } },
  twitter: { card: "summary_large_image", title: "AI for business", description: "Business AI: workflow audit, team training, bounded pilots and QA.", images: ["/opengraph-image"] },
};
export default function Page(){return <WorkshopBusiness locale="en"/>;}
