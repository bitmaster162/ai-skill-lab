import sections from "../data/phuket_housing_r6_sections.json";

export type HousingLocale = "ru" | "en";

/** Build-generated, reviewed empty inventory only. Never consumes browser input. */
export function withHousingCatalog(markup: string, locale: HousingLocale): string {
  if (locale !== "ru" && locale !== "en") throw new Error("Unknown housing locale");
  if (sections.schema !== "phuket-housing-sections.v1" || sections.listings_count !== 0
      || sections.input_sha256 !== "a9e2b3b604b03e2dba232506e65b0175c094428181af7e050fa10d812b1f428d") {
    throw new Error("Unreviewed R6 housing inventory");
  }
  const marker = 'id="homes"';
  const point = markup.indexOf(marker);
  const start = markup.lastIndexOf("<section ", point);
  const close = markup.indexOf("</section>", point);
  if (point < 0 || start < 0 || close < point || markup.indexOf(marker, point + marker.length) !== -1
      || markup.includes("data-u2-catalog")) throw new Error("Housing section boundary drift");
  const replacement = sections[locale];
  if (!replacement.startsWith("<section ") || !replacement.endsWith("</section>")
      || !replacement.includes('data-u2-catalog=""') || replacement.includes("data-u2-card")) {
    throw new Error("Invalid empty housing section");
  }
  return markup.slice(0, start) + replacement + markup.slice(close + "</section>".length);
}
