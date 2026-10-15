import Link from "next/link";

type Locale = "ru" | "en";

/** Semantic same-origin footer destination, no dependency on browser JavaScript. */
export function UniverseFooterLink({ locale }: { locale: Locale }) {
  const href = locale === "en" ? "/en/phuket-universe" : "/phuket-universe";
  return <Link className="workshopButton" href={href}
    data-universe-event="universe_click" aria-label={locale === "en" ? "Phuket Universe" : "????????? ???????"}>
    <svg viewBox="0 0 34 34" width="20" height="20" aria-hidden="true" fill="none"
      stroke="currentColor" strokeWidth="1.8">
      <ellipse cx="17" cy="17" rx="15" ry="9" transform="rotate(-16 17 17)" />
      <circle cx="17" cy="17" r="5" />
      <circle cx="30" cy="12.5" r="2.8" fill="currentColor" stroke="none" />
    </svg>{" "}Phuket Universe
  </Link>;
}
