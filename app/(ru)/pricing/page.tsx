import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { courseListSchema } from "@/lib/structured-data";
import { WorkshopPricing } from "@/components/workshop/WorkshopPricing";
export const metadata: Metadata = { title: { absolute: "Цены на обучение ИИ: сессии, пакеты, пилоты — AI Skill Lab" }, description: "Цены AI Skill Lab в долларах: бесплатный звонок 15 минут, диагностика $120, пакеты занятий по 60 минут, обучение команд и пилоты для бизнеса.", alternates: { canonical: "/pricing", languages: { ru: "/pricing", en: "/en/pricing" } } ,
  ...ogPageMetadata({ locale: "ru", slug: "pricing", title: "Цены на обучение ИИ: сессии, пакеты, пилоты — AI Skill Lab", description: "Цены AI Skill Lab в долларах: бесплатный звонок 15 минут, диагностика $120, пакеты занятий по 60 минут, обучение команд и пилоты для бизнеса." }),
};
export default function PricingPage(){return <><JsonLd data={courseListSchema("ru")} /><WorkshopPricing locale="ru"/></>}
