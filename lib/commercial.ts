import facts from "@/data/commercial_facts.json";

export type WorkshopLocale = "ru" | "en";
export type CommercialPlan = (typeof facts.tracks.adult)[number];

if (facts.schema !== "ai-skill-lab.commercial-facts.v2" || facts.version !== 2) {
  throw new Error("Unsupported commercial facts authority");
}
if (facts.session_duration_minutes !== 60) {
  throw new Error("Session duration authority must be 60 minutes");
}

export const commercialFacts = facts;
export const sessionDurationMinutes = facts.session_duration_minutes;

export function sessionLabel(plan: CommercialPlan, locale: WorkshopLocale) {
  return locale === "ru" ? plan.sessions_ru : plan.sessions_en;
}

export function summaryLabel(plan: CommercialPlan, locale: WorkshopLocale) {
  return locale === "ru" ? plan.summary_ru : plan.summary_en;
}

export function localizedName(value: { name_ru: string; name_en: string }, locale: WorkshopLocale) {
  return locale === "ru" ? value.name_ru : value.name_en;
}
