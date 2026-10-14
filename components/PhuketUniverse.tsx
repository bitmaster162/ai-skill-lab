import "@/app/phuket-universe.css";
import "@/app/phuket-universe-agency-terms.css";
import { withAgencyPilotTerms } from "@/components/phuketUniverseAgencyTerms";
import { phuketUniverseMarkup } from "@/components/phuketUniverseMarkup";

export type PhuketUniverseLocale = "ru" | "en";

/**
 * U1 is a fixed, reviewed HTML design snapshot, generated from the SHA-pinned
 * local mockup. It contains only static markup and embedded SVG, not user data.
 * Housing ingestion/filtering remains a separate U2 implementation.
 */
export function PhuketUniverse({ locale }: { locale: PhuketUniverseLocale }) {
  return (
    <div
      className="pu-page"
      lang={locale}
      data-phuket-universe={locale}
      dangerouslySetInnerHTML={{ __html: withAgencyPilotTerms(phuketUniverseMarkup[locale], locale) }}
    />
  );
}
