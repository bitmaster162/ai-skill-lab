import type { Metadata } from "next";
import "./globals.css";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: {
    default: "AI Skill Lab — персональное обучение искусственному интеллекту",
    template: "%s | AI Skill Lab",
  },
  description:
    "Практическое обучение AI 1-на-1 для взрослых, бизнеса, детей и подростков — Phuket и online: реальные проекты, research, automation и responsible AI.",
  metadataBase: new URL(site.url),
  openGraph: {
    title: "AI Skill Lab",
    description: "Персональное обучение AI 1-на-1 в Phuket и online через реальные задачи, workflows и собственные проекты.",
    type: "website",
    siteName: "AI Skill Lab",
    locale: "ru_RU",
    images: [{ url: "/opengraph-image", width: 1200, height: 630, alt: "AI Skill Lab" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "AI Skill Lab",
    description: "Практические AI-навыки через реальные задачи и проекты.",
    images: ["/opengraph-image"],
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
