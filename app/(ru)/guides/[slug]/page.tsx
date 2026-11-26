import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { GuideArticle } from "@/components/guides/GuidePages";
import { getGuide, listGuides } from "@/lib/guides";

import cards from "@/guides/aiskillab/social-cards.json";

const socialCards: Readonly<Record<string, { url: string; alt: string }>> = cards;

type Props = { params: Promise<{ slug: string }> };

export function generateStaticParams() {
  return listGuides("ru").map((guide) => ({ slug: guide.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const guide = getGuide("ru", slug);
  if (!guide) return {};
  const image = socialCards[guide.meta.path] ?? { url: "/og.png", alt: "AI Skill Lab · Phuket" };
  return {
    title: { absolute: guide.meta.seo_title },
    description: guide.meta.description,
    alternates: { canonical: guide.meta.path, languages: { ru: guide.meta.path, en: guide.meta.alternate, "x-default": guide.meta.path } },
    openGraph: {
      type: "article",
      title: guide.meta.seo_title,
      description: guide.meta.description,
      url: guide.meta.path,
      siteName: "AI Skill Lab · Phuket",
      locale: "ru_RU",
      alternateLocale: ["en_US"],
      images: [{ ...image, width: 1200, height: 630 }],
    },
    twitter: { card: "summary_large_image", title: guide.meta.seo_title, description: guide.meta.description, images: [image] },
  };
}

export default async function GuidePage({ params }: Props) {
  const { slug } = await params;
  const guide = getGuide("ru", slug);
  if (!guide) notFound();
  return <GuideArticle guide={guide} />;
}
