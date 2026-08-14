import Link from "next/link";
import { ArrowIcon } from "./ArrowIcon";

export function ContactButtons({ fallbackHref, locale = "ru" }: { fallbackHref?: string; locale?: "ru" | "en" }) {
  const resolvedFallback = fallbackHref || (locale === "en" ? "/en/start" : "/start");
  const matcherHref = locale === "en" ? "/en/matcher" : "/matcher";
  const copy = locale === "ru"
    ? { start: "Что написать", matcher: "Подобрать программу" }
    : { start: "What to send", matcher: "Find my program" };
  return (
    <div className="contactButtons">
      <Link className="button buttonLight" href={resolvedFallback}>{copy.start} <ArrowIcon /></Link>
      <Link className="button buttonGhost buttonOnDark" href={matcherHref}>{copy.matcher} <ArrowIcon /></Link>
    </div>
  );
}
