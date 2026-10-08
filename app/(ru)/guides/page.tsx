import type { Metadata } from "next";
import { GuideListing } from "@/components/guides/GuidePages";
import { listGuides } from "@/lib/guides";

export const metadata: Metadata = {
  title: { absolute: "Гайды по ИИ — AI Skill Lab · Пхукет" },
  description: "Короткие проверенные материалы об ИИ для родителей, взрослых учеников и команд. У каждого — дата проверки и источники.",
  alternates: { canonical: "/guides", languages: { ru: "/guides", en: "/en/guides", "x-default": "/guides" } },
};

export default function GuidesPage() {
  return <GuideListing locale="ru" guides={listGuides("ru")} />;
}
