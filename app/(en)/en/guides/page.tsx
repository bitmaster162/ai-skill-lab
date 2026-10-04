import type { Metadata } from "next";
import { GuideListing } from "@/components/guides/GuidePages";
import { listGuides } from "@/lib/guides";

export const metadata: Metadata = {
  title: "Guides",
  description: "Short, checked guides for parents, adult learners and teams. Each one shows when it was checked and its sources.",
  alternates: { canonical: "/en/guides", languages: { ru: "/guides", en: "/en/guides", "x-default": "/guides" } },
};

export default function GuidesPageEn() {
  return <GuideListing locale="en" guides={listGuides("en")} />;
}
