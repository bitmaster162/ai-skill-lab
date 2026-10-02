import type { Metadata, Viewport } from "next";
import "../globals.css";
import "../r69.css";
import "../r70.css";
import "../commercial-mobile.css";
import "../proof-contrast.css";
import { site } from "@/lib/site";
import { JsonLd } from "@/components/JsonLd";
import { organizationSchemaEn } from "@/lib/structured-data";

export const metadata: Metadata = {
  title: {
    default: "AI Skill Lab · Phuket — practical AI learning",
    template: "%s | AI Skill Lab · Phuket",
  },
  description:
    "Practical one-to-one AI learning for adults, business, kids and teens — in Phuket and online through real projects, research, automation and responsible AI.",
  metadataBase: new URL(site.url),
  openGraph: {
    title: "AI Skill Lab · Phuket",
    description: "One-to-one practical AI learning in Phuket and online through real tasks, workflows and learner-built projects.",
    type: "website",
    siteName: "AI Skill Lab · Phuket",
    locale: "en_US",
    alternateLocale: ["ru_RU"],
    images: [{ url: "/og.png", width: 1200, height: 630, alt: "AI Skill Lab · Phuket" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "AI Skill Lab · Phuket",
    description: "Practical AI skills through real tasks and projects.",
    images: ["/og.png"],
  },
  manifest: "/site.webmanifest",
  icons: {
    icon: [{ url: "/favicon.svg", type: "image/svg+xml" }],
    shortcut: [{ url: "/favicon.ico" }],
    apple: [{ url: "/apple-touch-icon.png", sizes: "180x180", type: "image/png" }],
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
    <html lang="en">
      <head>
        <link rel="preload" href="/fonts/Onest-ru-en.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
        <link rel="preload" href="/fonts/Unbounded-ru-en.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
      </head>
      <body><JsonLd data={organizationSchemaEn} />{children}<script defer src="/_vercel/insights/script.js" /></body>
    </html>
  );
}
