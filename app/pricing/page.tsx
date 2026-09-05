import type { Metadata } from "next";
import { WorkshopPricing } from "@/components/workshop/WorkshopPricing";
export const metadata: Metadata = { title: "Стоимость и форматы", description: "Прозрачные цены AI Skill Lab: сессии 60 минут, персональные пакеты, бизнес-пилоты и ограниченное сопровождение.", alternates: { canonical: "/pricing", languages: { ru: "/pricing", en: "/en/pricing" } } };
export default function PricingPage(){return <WorkshopPricing locale="ru"/>}
