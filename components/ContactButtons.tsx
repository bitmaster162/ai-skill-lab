import Link from "next/link";

type Locale = "ru" | "en";

export function ContactButtons({ fallbackHref = "#contact", locale = "ru" }: { fallbackHref?: string; locale?: Locale }) {
  const telegram = process.env.NEXT_PUBLIC_TELEGRAM_URL || "https://t.me/BiTFormer";
  const whatsapp = process.env.NEXT_PUBLIC_WHATSAPP_URL;
  const labels = locale === "ru"
    ? { tg: "Написать в Telegram", wa: "Написать в WhatsApp", form: "Оставить заявку" }
    : { tg: "Message on Telegram", wa: "Message on WhatsApp", form: "Send an application" };

  return (
    <div className="contactButtons">
      <a className="button buttonPrimary" href={telegram} target="_blank" rel="noreferrer">{labels.tg}</a>
      {whatsapp ? (
        <a className="button buttonGhost buttonOnDark" href={whatsapp} target="_blank" rel="noreferrer">{labels.wa}</a>
      ) : (
        <Link className="button buttonGhost buttonOnDark" href={fallbackHref}>{labels.form}</Link>
      )}
    </div>
  );
}
