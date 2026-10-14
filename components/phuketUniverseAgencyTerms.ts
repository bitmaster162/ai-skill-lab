import terms from "../data/phuket_universe_agency_pilot_terms_r1.json";

export type AgencyTermsLocale = "ru" | "en";
const marker = '<a class="pu-s101" href="mailto:robert@aiskillab.work?subject=';
const versionMarker = 'data-agency-terms-version="pilot-r1"';

function escapeText(value: string): string {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#x27;");
}

/** Fixed source-report copy. No user HTML, API requests or paid-plan activation. */
export function withAgencyPilotTerms(markup: string, locale: AgencyTermsLocale): string {
  if (locale !== "ru" && locale !== "en") throw new Error("Unknown agency terms locale");
  if (terms.version !== "pilot-r1" || terms.schema !== "phuket-universe.agency-pilot-copy.v1") {
    throw new Error("Agency terms version mismatch");
  }
  const copy = terms[locale];
  if (copy.paragraphs.length !== 3 || !copy.summary || copy.paragraphs.some(p => !p.trim())) {
    throw new Error("Incomplete source-report copy");
  }
  const section = markup.indexOf('id="agencies"');
  const sectionEnd = markup.indexOf("</section>", section);
  const index = markup.indexOf(marker);
  if (markup.includes(versionMarker) || section < 0 || sectionEnd < 0 || index < section
      || index > sectionEnd || markup.indexOf(marker, index + marker.length) !== -1) {
    throw new Error("Agency section boundary drift or duplicate terms");
  }
  const block = '<details class="pu-agency-terms" id="agency-pilot-terms" ' + versionMarker + '>'
    + '<summary>' + escapeText(copy.summary) + '</summary><div class="pu-agency-terms-body">'
    + copy.paragraphs.map(text => '<p>' + escapeText(text) + '</p>').join("")
    + '</div></details>\n';
  return markup.slice(0, index) + block + markup.slice(index);
}
