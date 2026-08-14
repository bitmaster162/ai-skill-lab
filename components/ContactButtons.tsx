import Link from "next/link";
import { site } from "@/lib/site";
import { ArrowIcon } from "./ArrowIcon";

export function ContactButtons({ fallbackHref, locale = "ru" }: { fallbackHref?: string; locale?: "ru" | "en" }) {
  const resolvedFallback = fallbackHref || (locale === "en" ? "/en/start" : "/start");
  const copy = locale === "ru"
    ? { tg: "Написать в Telegram", wa: "Написать в WhatsApp", form: "Оставить заявку" }
    : { tg: "Message on Telegram", wa: "Message on WhatsApp", form: "Send an application" };
  return (
    <div className="contactButtons">
      <a className="button buttonLight" href={site.telegram} target="_blank" rel="noreferrer">{copy.tg} <ArrowIcon /></a>
      {site.whatsapp ? <a className="button buttonGhost buttonOnDark" href={site.whatsapp} target="_blank" rel="noreferrer">{copy.wa} <ArrowIcon /></a> : null}
      <Link className="textLink textLinkLight" href={resolvedFallback}>{copy.form} <ArrowIcon /></Link>
    </div>
  );
}
