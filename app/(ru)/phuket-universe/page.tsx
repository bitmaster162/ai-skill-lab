import type { Metadata } from "next";
import { PhuketUniverse } from "@/components/PhuketUniverse";

const title = "Вселенная Пхукета — Phuket Universe | AI Skill Lab";
const description = "Проекты знакомых людей на Пхукете и будущие объекты агентств-партнёров: карта острова, контакты и прямые ссылки на владельцев.";

export const metadata: Metadata = {
  title: { absolute: "Вселенная Пхукета — Phuket Universe | AI Skill Lab" },
  description: "Проекты знакомых людей на Пхукете и будущие объекты агентств-партнёров: карта острова, контакты и прямые ссылки на владельцев.",
  alternates: {
    canonical: "/phuket-universe",
    languages: { ru: "/phuket-universe", en: "/en/phuket-universe" },
  },
  openGraph: {
    title,
    description,
    url: "/phuket-universe",
    locale: "ru_RU",
    alternateLocale: "en_US",
    type: "website",
  },
};

export default function Page() {
  return <PhuketUniverse locale="ru" />;
}
