import Link from "next/link";
import { Logo } from "./Logo";

type Locale = "ru" | "en";

type HeaderProps = {
  contactHref?: string;
  locale?: Locale;
  alternateHref?: string;
};

const labels = {
  ru: {
    programs: "Программы",
    kids: "Дети 8–13",
    teens: "Подростки 14–18",
    pricing: "Стоимость",
    faq: "FAQ",
    cta: "Подобрать программу",
    menu: "Меню",
    lang: "EN",
  },
  en: {
    programs: "Programs",
    kids: "Kids 8–13",
    teens: "Teens 14–18",
    pricing: "Pricing",
    faq: "FAQ",
    cta: "Find my program",
    menu: "Menu",
    lang: "RU",
  },
};

export function Header({ contactHref, locale = "ru", alternateHref }: HeaderProps) {
  const t = labels[locale];
  const base = locale === "ru" ? "" : "/en";
  const home = base || "/";
  const contact = contactHref || `${base}/#contact`;
  const alternate = alternateHref || (locale === "ru" ? "/en" : "/");

  return (
    <header className="siteHeader">
      <div className="shell headerInner">
        <Logo href={home} />
        <nav className="desktopNav" aria-label={locale === "ru" ? "Основная навигация" : "Main navigation"}>
          <Link href={`${base}/#programs`}>{t.programs}</Link>
          <Link href={`${base}/kids`}>{t.kids}</Link>
          <Link href={`${base}/teens`}>{t.teens}</Link>
          <Link href={`${base}/#pricing`}>{t.pricing}</Link>
          <Link href={`${base}/#faq`}>{t.faq}</Link>
        </nav>
        <div className="headerActions">
          <Link className="langSwitch" href={alternate}>{t.lang}</Link>
          <Link className="button buttonSmall buttonGhost headerCta" href={contact}>{t.cta}</Link>
          <details className="mobileMenu">
            <summary aria-label={t.menu}><span /><span /><span /></summary>
            <nav>
              <Link href={`${base}/#programs`}>{t.programs}</Link>
              <Link href={`${base}/kids`}>{t.kids}</Link>
              <Link href={`${base}/teens`}>{t.teens}</Link>
              <Link href={`${base}/#pricing`}>{t.pricing}</Link>
              <Link href={`${base}/#faq`}>{t.faq}</Link>
              <Link href={contact}>{t.cta}</Link>
            </nav>
          </details>
        </div>
      </div>
    </header>
  );
}
