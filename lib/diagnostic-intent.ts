// The start form carries inquiry intent. It never establishes payment or consent.
export function startInquiryProgram(pathname: string | null, params: Pick<URLSearchParams, "getAll"> | null): "" | "diagnostic" {
  if (pathname !== "/start" && pathname !== "/en/start") return "";
  const values = params?.getAll("program") ?? [];
  return values.length === 1 && values[0] === "diagnostic" ? "diagnostic" : "";
}

export function diagnosticApplicationHref(locale: "ru" | "en"): string {
  return `${locale === "en" ? "/en" : ""}/start?program=diagnostic#application-form`;
}
