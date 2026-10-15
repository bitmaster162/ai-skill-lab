export type UniverseLocale = "ru" | "en";

const friends = [
  "phuketravel.vercel.app",
  "stasph.vercel.app",
  "muaithaiph.vercel.app",
  "haven-ruddy.vercel.app",
  "rostikson-portfolio.vercel.app",
] as const;

/** Add exactly five project-card markers and a real Universe footer link. */
export function withUniverseU3(markup: string, locale: UniverseLocale): string {
  if (locale !== "ru" && locale !== "en") throw new Error("Unknown Universe locale");
  if (markup.includes('data-universe-event="project_click"')
      || markup.includes('data-universe-event="universe_click"')) {
    throw new Error("Duplicate U3 tracking markers");
  }
  const orbitIndex = markup.indexOf('id="orbit"');
  const homesIndex = markup.indexOf('id="homes"');
  if (orbitIndex < 0 || homesIndex < orbitIndex) throw new Error("U3 section boundaries");
  let orbit = markup.slice(orbitIndex, homesIndex);
  for (const domain of friends) {
    const original = 'class="pu-s053" rel="noopener" href="https://' + domain + '"';
    if (orbit.split(original).length !== 2) throw new Error("Unexpected U3 project card: " + domain);
    orbit = orbit.replace(original, 'class="pu-s053" data-universe-event="project_click" rel="noopener" href="https://' + domain + '"');
  }
  const footerOriginal = '<a class="pu-s112" href="#top">';
  if (markup.split(footerOriginal).length !== 2) throw new Error("U3 footer anchor missing");
  const href = locale === "en" ? "/en/phuket-universe" : "/phuket-universe";
  const withCards = markup.slice(0, orbitIndex) + orbit + markup.slice(homesIndex);
  return withCards.replace(footerOriginal, '<a class="pu-s112" data-universe-event="universe_click" href="' + href + '">');
}
