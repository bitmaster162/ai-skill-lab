import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { GuideArticle } from "@/components/guides/GuidePages";
import { getGuide, listGuides } from "@/lib/guides";

type Props = { params: Promise<{ slug: string }> };

export function generateStaticParams() {
  return listGuides("ru").map((guide) => ({ slug: guide.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const guide = getGuide("ru", slug);
  if (!guide) return {};
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
      images: [{ url: "/og.png", width: 1200, height: 630, alt: "AI Skill Lab · Phuket" }],
    },
    twitter: { card: "summary_large_image", title: guide.meta.seo_title, description: guide.meta.description, images: ["/og.png"] },
  };
}

export default async function GuidePage({ params }: Props) {
  const { slug } = await params;
  const guide = getGuide("ru", slug);
  if (!guide) notFound();
  return <GuideArticle guide={guide} />;
}
