import "@/app/phuket-universe.css";
import "@/app/phuket-universe-agency-terms.css";
import "@/public/phuket-housing-u2.css";
import { withAgencyPilotTerms } from "@/components/phuketUniverseAgencyTerms";
import { phuketUniverseMarkup } from "@/components/phuketUniverseMarkup";
import { withHousingCatalog } from "@/components/phuketHousingCatalog";
import { PhuketHousingRuntime } from "@/components/PhuketHousingRuntime";

export type PhuketUniverseLocale = "ru" | "en";

/** Fixed SVG design, report-based terms and reviewed empty U2 build snapshot. */
export function PhuketUniverse({ locale }: { locale: PhuketUniverseLocale }) {
  const markup = withHousingCatalog(withAgencyPilotTerms(phuketUniverseMarkup[locale], locale), locale);
  return <>
    <div className="pu-page" lang={locale} data-phuket-universe={locale}
      dangerouslySetInnerHTML={{ __html: markup }} />
    <PhuketHousingRuntime />
  </>;
}
