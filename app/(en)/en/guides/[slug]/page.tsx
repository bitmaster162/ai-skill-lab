import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { GuideArticle } from "@/components/guides/GuidePages";
import { getGuide, listGuides } from "@/lib/guides";

type Props = { params: Promise<{ slug: string }> };

export function generateStaticParams() {
  return listGuides("en").map((guide) => ({ slug: guide.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const guide = getGuide("en", slug);
  if (!guide) return {};
  return {
    title: { absolute: guide.meta.seo_title },
    description: guide.meta.description,
    alternates: { canonical: guide.meta.path, languages: { ru: guide.meta.alternate, en: guide.meta.path, "x-default": guide.meta.alternate } },
    openGraph: {
      type: "article",
      title: guide.meta.seo_title,
      description: guide.meta.description,
      url: guide.meta.path,
      siteName: "AI Skill Lab · Phuket",
      locale: "en_US",
      alternateLocale: ["ru_RU"],
      images: [{ url: "/og.png", width: 1200, height: 630, alt: "AI Skill Lab · Phuket" }],
    },
    twitter: { card: "summary_large_image", title: guide.meta.seo_title, description: guide.meta.description, images: ["/og.png"] },
  };
}

export default async function GuidePageEn({ params }: Props) {
  const { slug } = await params;
  const guide = getGuide("en", slug);
  if (!guide) notFound();
  return <GuideArticle guide={guide} />;
}
