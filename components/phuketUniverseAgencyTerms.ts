export type AgencyTermsLocale = "ru" | "en";
const marker = '<a class="pu-s101" href="mailto:robert@aiskillab.work?subject=';
const duplicateMarker = 'id="agency-listing-terms"';

const copy: Record<AgencyTermsLocale, string> = {
  ru: "Условия размещения обсуждаем индивидуально — напишите нам.",
  en: "Listing terms are discussed individually — write to us.",
};
function escapeText(value: string): string {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#x27;");
}
/** Single owner-approved note; no partnership, price or pilot obligations. */
export function withAgencyPilotTerms(markup: string, locale: AgencyTermsLocale): string {
  if (locale !== "ru" && locale !== "en") throw new Error("Unknown agency terms locale");
  const section = markup.indexOf('id="agencies"');
  const sectionEnd = markup.indexOf("</section>", section);
  const index = markup.indexOf(marker);
  if (markup.includes(duplicateMarker) || markup.includes('id="agency-pilot-terms"')
      || section < 0 || sectionEnd < 0 || index < section
      || index > sectionEnd || markup.indexOf(marker, index + marker.length) !== -1) {
    throw new Error("Agency section boundary drift or duplicate listing note");
  }
  const block = '<p class="pu-agency-terms" ' + duplicateMarker + '>'
    + escapeText(copy[locale]) + '</p>\n';
  return markup.slice(0, index) + block + markup.slice(index);
}
