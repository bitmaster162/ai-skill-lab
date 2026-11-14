"use client";

import { useSearchParams } from "next/navigation";
import { selectStartProgram } from "@/lib/diagnostic-intent";
import { LeadForm } from "./LeadForm";

export function StartLeadForm({ locale }: { locale: "ru" | "en" }) {
  const searchParams = useSearchParams();
  // SSR fallback is generic; the selected inquiry appears only after hydration.
  // Unknown and repeated query values cannot select another track.
  const values = searchParams.getAll("program");
  const program = values.length === 1 ? selectStartProgram(values[0]) : "";
  return <LeadForm locale={locale} program={program} />;
}
