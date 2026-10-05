import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { courseListSchema } from "@/lib/structured-data";
import { WorkshopPricing } from "@/components/workshop/WorkshopPricing";
export const metadata: Metadata = { title: { absolute: "Стоимость и форматы — AI Skill Lab · Phuket" }, description: "Прозрачные цены AI Skill Lab: сессии 60 минут, персональные пакеты, бизнес-пилоты и ограниченное сопровождение.", alternates: { canonical: "/pricing", languages: { ru: "/pricing", en: "/en/pricing" } } ,
  ...ogPageMetadata({ locale: "ru", slug: "pricing", title: "Стоимость и форматы — AI Skill Lab · Phuket", description: "Прозрачные цены AI Skill Lab: сессии 60 минут, персональные пакеты, бизнес-пилоты и ограниченное сопровождение." }),
};
export default function PricingPage(){return <><JsonLd data={courseListSchema("ru")} /><WorkshopPricing locale="ru"/></>}
