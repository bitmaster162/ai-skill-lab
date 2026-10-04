import type { Metadata } from "next";
import { GuideListing } from "@/components/guides/GuidePages";
import { listGuides } from "@/lib/guides";

export const metadata: Metadata = {
  title: "Гайды",
  description: "Короткие проверенные материалы для родителей, взрослых учеников и команд. У каждого — дата проверки и источники.",
  alternates: { canonical: "/guides", languages: { ru: "/guides", en: "/en/guides", "x-default": "/guides" } },
};

export default function GuidesPage() {
  return <GuideListing locale="ru" guides={listGuides("ru")} />;
}
