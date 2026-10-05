import type { Metadata } from "next";

export type OgLocale = "ru" | "en";
export type OgSlug = "home" | "pricing" | "start" | "kids" | "teens" | "parents" | "personal" | "business" | "phuket" | "faq";

const OG_ALT: Record<OgLocale, Record<OgSlug, string>> = {
  ru: {
    home: "Освойте AI так, чтобы результат остался у вас.",
    pricing: "Знайте цену. Фиксируйте scope.",
    start: "Сначала fit. Потом программа.",
    kids: "AI — не кнопка «сделай за меня».",
    teens: "Не просто пользоваться AI. Собирать и объяснять.",
    parents: "Платить не за «ребёнок поиграл с AI».",
    personal: "Не курс про AI, а ваш рабочий процесс.",
    business: "Не «добавить AI». Изменить один процесс.",
    phuket: "Локально на Phuket. И без географии online.",
    faq: "Одиннадцать ответов до разговора.",
  },
  en: {
    home: "Learn AI so the capability stays with you.",
    pricing: "Know the price. Define the scope.",
    start: "Fit first. Program second.",
    kids: "AI is not a button that does it for you.",
    teens: "Do more than use AI. Build it. Explain it.",
    parents: "Do not pay for “my child played with AI.”",
    personal: "Not a course about AI. Your own working system.",
    business: "Do not add AI. Change one process.",
    phuket: "Local in Phuket. Borderless online.",
    faq: "Eleven answers before the call.",
  },
};

function routePath(locale: OgLocale, slug: OgSlug): string {
  if (slug === "home") return locale === "ru" ? "/" : "/en";
  return locale === "ru" ? `/${slug}` : `/en/${slug}`;
}

export function ogPageMetadata(args: {
  locale: OgLocale;
  slug: OgSlug;
  title: string;
  description: string;
}): Pick<Metadata, "openGraph" | "twitter"> {
  const { locale, slug, title, description } = args;
  const image = `/og-${locale}-${slug}.png`;
  return {
    openGraph: {
      title,
      description,
      type: "website",
      siteName: "AI Skill Lab · Phuket",
      locale: locale === "ru" ? "ru_RU" : "en_US",
      alternateLocale: [locale === "ru" ? "en_US" : "ru_RU"],
      url: routePath(locale, slug),
      images: [{ url: image, width: 1200, height: 630, alt: OG_ALT[locale][slug] }],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [image],
    },
  };
}
