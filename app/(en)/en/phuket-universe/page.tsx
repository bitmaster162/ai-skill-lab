import type { Metadata } from "next";
import { PhuketUniverse } from "@/components/PhuketUniverse";

const title = "Phuket Universe — Projects & Homes | AI Skill Lab · Phuket";
const description = "Explore projects by people we know in Phuket and forthcoming partner-home listings on an island map, with direct links to project owners.";

export const metadata: Metadata = {
  title: { absolute: "Phuket Universe — Projects & Homes | AI Skill Lab · Phuket" },
  description: "Explore projects by people we know in Phuket and forthcoming partner-home listings on an island map, with direct links to project owners.",
  alternates: {
    canonical: "/en/phuket-universe",
    languages: { ru: "/phuket-universe", en: "/en/phuket-universe" },
  },
  openGraph: {
    title,
    description,
    url: "/en/phuket-universe",
    locale: "en_US",
    alternateLocale: "ru_RU",
    type: "website",
  },
};

export default function Page() {
  return <PhuketUniverse locale="en" />;
}
