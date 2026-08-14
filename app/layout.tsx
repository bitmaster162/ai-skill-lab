import type { Metadata } from "next";
import "./globals.css";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: {
    default: "AI Skill Lab — персональное обучение искусственному интеллекту",
    template: "%s | AI Skill Lab",
  },
  description:
    "Практическое обучение AI для взрослых, детей, подростков и команд: индивидуальные программы, реальные проекты и ответственное использование инструментов.",
  metadataBase: new URL(site.url),
  openGraph: {
    title: "AI Skill Lab",
    description: "Персональное обучение AI через реальные задачи и собственные проекты.",
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
