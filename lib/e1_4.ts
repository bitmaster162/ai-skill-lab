import { commercialFacts, sessionDurationMinutes, type WorkshopLocale } from "./commercial";

export const introCall = {
  durationMinutes: 15,
  whatsappNumber: "66649701204",
  telegramUrl: "https://t.me/BiTFormer",
  label: { ru: "Бесплатный звонок-знакомство · 15 минут", en: "Free 15-minute intro call" },
  freeMeta: { ru: "Бесплатно · 15 минут", en: "Free · 15 minutes" },
  whatsappMessage: {
    ru: "Здравствуйте! Хочу записаться на бесплатный звонок-знакомство, 15 минут.",
    en: "Hi! I'd like to book the free 15-minute intro call.",
  },
} as const;

export function introWhatsappHref(locale: WorkshopLocale) {
  return `https://wa.me/${introCall.whatsappNumber}?text=${encodeURIComponent(introCall.whatsappMessage[locale])}`;
}

export function diagnosticCtaSummary(locale: WorkshopLocale) {
  const d = commercialFacts.diagnostic;
  return locale === "en"
    ? `Diagnostic session ${d.price} · ${sessionDurationMinutes} minutes · ${d.credit_en}`
    : `Диагностика ${d.price} · ${sessionDurationMinutes} минут · ${d.credit_ru}`;
}
