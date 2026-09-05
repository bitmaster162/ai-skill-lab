import Link from "next/link";
import { LabCommand } from "@/components/LabCommand";
import styles from "./WorkshopShell.module.css";

export type WorkshopLocale = "ru" | "en";

type Props = {
  locale?: WorkshopLocale;
  alternateHref: string;
  contactHref?: string;
  children: React.ReactNode;
};

const menu = {
  ru: [["Взрослые", "/personal"], ["Подростки", "/teens"], ["Дети", "/kids"], ["Бизнес", "/business"], ["Studio", "/studio"], ["Цены", "/pricing"]],
  en: [["Adults", "/en/personal"], ["Teens", "/en/teens"], ["Kids", "/en/kids"], ["Business", "/en/business"], ["Studio", "/en/studio"], ["Pricing", "/en/pricing"]],
} as const;

export function WorkshopShell({ locale = "ru", alternateHref, contactHref, children }: Props) {
  const en = locale === "en";
  const home = en ? "/en" : "/";
  const start = contactHref || (en ? "/en/start" : "/start");
  return (
    <div className={styles.page}>
      <a className={styles.skip} href="#main">{en ? "Skip to content" : "К содержанию"}</a>
      <header className={styles.header}>
        <Link className={styles.brand} href={home} aria-label="AI Skill Lab — Home">
          <span className={styles.mark} aria-hidden="true">A</span><span>AI SKILL LAB</span>
        </Link>
        <nav className={styles.menu} aria-label={en ? "Main navigation" : "Основная навигация"}>
          {menu[locale].map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}
        </nav>
        <div className={styles.actions}>
          <Link className={styles.utility} href={en ? "/en/proof" : "/proof"} aria-label="Proof Lab">LAB</Link>
          <LabCommand locale={locale} />
          <Link className={styles.utility} href={alternateHref}>{en ? "RU" : "EN"}</Link>
          <Link className={styles.primary} href={start}>{en ? "Start" : "Начать"}</Link>
        </div>
      </header>
      {children}
      <footer className={styles.footer}>
        <div><strong>AI Skill Lab</strong><span>{en ? "Practical AI capability · online / Phuket" : "Практический AI · online / Phuket"}</span></div>
        <nav aria-label={en ? "Footer" : "Подвал"}>
          <Link href={en ? "/en/faq" : "/faq"}>FAQ</Link>
          <Link href={en ? "/en/about" : "/about"}>{en ? "About" : "О проекте"}</Link>
          <Link href={en ? "/en/challenge" : "/challenge"}>Challenge</Link>
          <Link href={en ? "/en/build" : "/build"}>Build Log</Link>
          <Link href={en ? "/en/proof" : "/proof"}>Proof Lab</Link>
        </nav>
        <span>© 2026</span>
      </footer>
    </div>
  );
}
