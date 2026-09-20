import type { Metadata, Viewport } from "next";
import "../globals.css";
import "../r69.css";
import "../r70.css";
import "../commercial-mobile.css";
import "../proof-contrast.css";
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
    images: [{ url: "/og.png", width: 1200, height: 630, alt: "AI Skill Lab" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "AI Skill Lab",
    description: "Практические AI-навыки через реальные задачи и проекты.",
    images: ["/og.png"],
  },
  manifest: "/site.webmanifest",
  icons: {
    icon: [{ url: "/favicon.svg", type: "image/svg+xml" }],
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#0b0d10",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ru">
      <head>
        <link rel="preload" href="/fonts/Onest-ru-en.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
        <link rel="preload" href="/fonts/Unbounded-ru-en.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
