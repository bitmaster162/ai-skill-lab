import type { Metadata } from "next";
import "./globals.css";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://example.com";

export const metadata: Metadata = {
  title: {
    default: "AI Skill Lab — персональное обучение искусственному интеллекту",
    template: "%s | AI Skill Lab",
  },
  description:
    "Практическое обучение AI для взрослых, детей, подростков и команд: индивидуальные программы, реальные проекты и ответственное использование инструментов.",
  metadataBase: new URL(siteUrl),
  openGraph: {
    title: "AI Skill Lab",
    description: "Персональное обучение AI через реальные задачи и собственные проекты.",
    type: "website",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
