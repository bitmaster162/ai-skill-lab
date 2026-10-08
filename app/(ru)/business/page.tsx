import type { Metadata } from "next";
import { ogPageMetadata } from "@/lib/og-assets";
import { JsonLd } from "@/components/JsonLd";
import { coursePageSchema } from "@/lib/structured-data";
import { WorkshopBusiness } from "@/components/workshop/WorkshopBusiness";
export const metadata: Metadata = {
  title: { absolute: "ИИ для бизнеса на Пхукете: обучение команды — AI Skill Lab" },
  description: "Обучение команды работе с ИИ, разбор процессов и один пилот — от выбора задачи до проверяемого результата, без лишних обещаний. Пхукет и онлайн.",
  alternates: { canonical: "/business", languages: { ru: "/business", en: "/en/business" } },
  twitter: { card: "summary_large_image", title: "AI для бизнеса", description: "Обучение команды работе с ИИ, разбор процессов и один пилот — от выбора задачи до проверяемого результата, без лишних обещаний. Пхукет и онлайн.", images: ["/og.png"] },

  ...ogPageMetadata({ locale: "ru", slug: "business", title: "ИИ для бизнеса на Пхукете: обучение команды — AI Skill Lab", description: "Обучение команды работе с ИИ, разбор процессов и один пилот — от выбора задачи до проверяемого результата, без лишних обещаний. Пхукет и онлайн." }),
};
export default function Page(){return <><JsonLd data={coursePageSchema("business", "ru")} /><WorkshopBusiness locale="ru"/></>;}
