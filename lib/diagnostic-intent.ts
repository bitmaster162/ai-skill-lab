// Only explicit diagnostic inquiries select a paid diagnostic intent on /start.
// A query parameter is not evidence of purchase, pricing acceptance, or consent.
export const START_PROGRAMS = ["", "diagnostic"] as const;
export type StartProgram = (typeof START_PROGRAMS)[number];

export function selectStartProgram(candidate: string | null): StartProgram {
  return candidate === "diagnostic" ? "diagnostic" : "";
}

export function diagnosticApplicationHref(locale: "ru" | "en"): string {
  return `${locale === "en" ? "/en" : ""}/start?program=diagnostic#application-form`;
}
