import Link from "next/link";
import { LabCommand } from "@/components/LabCommand";
import styles from "./WorkshopShell.module.css";

export type WorkshopLocale = "ru" | "en";

type Props = {
  locale?: WorkshopLocale;
  alternateHref: string;
  contactHref?: string;
  showReach?: boolean;
  light?: boolean;
  children: React.ReactNode;
};

const menu = {
  ru: [["Взрослые", "/personal"], ["Подростки", "/teens"], ["Дети", "/kids"], ["Бизнес", "/business"], ["Студия", "/studio"], ["Цены", "/pricing"]],
  en: [["Adults", "/en/personal"], ["Teens", "/en/teens"], ["Kids", "/en/kids"], ["Business", "/en/business"], ["Studio", "/en/studio"], ["Pricing", "/en/pricing"]],
} as const;

function ReachBlock({ locale }: { locale: WorkshopLocale }) {
  const en = locale === "en";
  return (
    <section className={styles.reachBlock}>
      <div className={styles.reachIntro}>
        <h2>{en ? "How to reach us" : "Как написать"}</h2>
        <p>{en ? "Use the application form or a direct channel; for a minor, coordination stays with an adult." : "Оставьте заявку или используйте прямой канал; для несовершеннолетнего контакт ведёт взрослый."}</p>
      </div>
      <div className={styles.reachActions}>
        <Link className={styles.reachStart} href={en ? "/en/start" : "/start"}>{en ? "Start application" : "Открыть заявку"}</Link>
      </div>
      <div className={styles.reachChannels}>
        <a href="https://t.me/BiTFormer" target="_blank" rel="noopener noreferrer">Telegram</a>
        <a href="https://wa.me/66649701204" target="_blank" rel="noopener noreferrer"><strong>WhatsApp</strong><span>+66 64 970 1204</span></a>
        <a href="https://line.me/ti/p/~iwf555" target="_blank" rel="noopener noreferrer"><strong>LINE</strong><span>iwf555</span></a>
        <a href="mailto:robert@aiskillab.work"><strong>{en ? "Email" : "Почта"}</strong><span>robert@aiskillab.work</span></a>
      </div>
      <p className={styles.reachReply}>{en ? "Reply within 1–2 business days." : "Ответ в течение 1–2 рабочих дней."}</p>
    </section>
  );
}

export function WorkshopShell({ locale = "ru", alternateHref, showReach = true, light = false, children }: Props) {
  const en = locale === "en";
  const home = en ? "/en" : "/";
  const start = en ? "/en/start" : "/start";
  return (
    <div className={`${styles.page} ${light ? styles.light : ""}`}>
      <a className={styles.skip} href="#main">{en ? "Skip to content" : "К содержанию"}</a>
      <header className={styles.header}>
        <Link className={styles.brand} href={home} aria-label="AI Skill Lab — Home">
          <span className={styles.mark} aria-hidden="true"><svg viewBox="0 0 24 24"><path fillRule="evenodd" d="M12 1 23 23H1Zm-1 9h2L16 14H8Zm-1.5 6h5L19 23H5Z" /></svg></span><span>AI SKILL LAB</span>
        </Link>
        <input
          className={styles.mobileMenuToggle}
          type="checkbox"
          id="workshop-menu"
          aria-label={en ? "Open menu" : "Открыть меню"}
          aria-controls="workshop-nav"
        />
        <label className={styles.burger} htmlFor="workshop-menu" aria-hidden="true"><span /><span /><span /></label>
        <nav id="workshop-nav" className={styles.menu} aria-label={en ? "Main navigation" : "Основная навигация"}>
          {menu[locale].map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}
        </nav>
        <div className={styles.actions}>
          <Link className={styles.utility} href={en ? "/en/proof" : "/proof"} aria-label={en ? "Proof Lab" : "Инструменты"}>{en ? "LAB" : "Инструменты"}</Link>
          <LabCommand locale={locale} />
          <Link className={styles.utility} href={alternateHref}>{en ? "RU" : "EN"}</Link>
          <Link className={styles.primary} href={start}>{en ? "Start application" : "Открыть заявку"}</Link>
        </div>
      </header>
      {children}
      {showReach ? <ReachBlock locale={locale} /> : null}
      <footer className={styles.footer}>
        <div><strong>AI Skill Lab</strong><span>{en ? "Practical AI capability · online / Phuket" : "Практический ИИ · онлайн / Пхукет"}</span></div>
        <nav aria-label={en ? "Footer" : "Подвал"}>
          <Link href={en ? "/en/faq" : "/faq"}>{en ? "FAQ" : "Вопросы"}</Link>
          <Link href={en ? "/en/guides" : "/guides"}>{en ? "Guides" : "Гайды"}</Link>
          <Link href={en ? "/en/about" : "/about"}>{en ? "About" : "О проекте"}</Link>
          <Link href={en ? "/en/challenge" : "/challenge"}>{en ? "Challenge" : "Задание"}</Link>
          <Link href={en ? "/en/build" : "/build"}>{en ? "Build Log" : "Как сделан сайт"}</Link>
          <Link href={en ? "/en/proof" : "/proof"}>{en ? "Proof Lab" : "Примеры и проверка"}</Link>
          <Link href={en ? "/en/pricing" : "/pricing"}>{en ? "Pricing" : "Цены"}</Link>
          <Link href={en ? "/en/start" : "/start"}>{en ? "Start application" : "Открыть заявку"}</Link>
          <Link href={en ? "/en/kids" : "/kids"}>{en ? "Kids" : "Дети"}</Link>
          <Link href={en ? "/en/teens" : "/teens"}>{en ? "Teens" : "Подростки"}</Link>
          <Link href={en ? "/en/parents" : "/parents"}>{en ? "For parents" : "Родителям"}</Link>
          <Link href={en ? "/en/personal" : "/personal"}>{en ? "Adults" : "Взрослые"}</Link>
          <Link href={en ? "/en/business" : "/business"}>{en ? "Business" : "Бизнес"}</Link>
        </nav>
        <nav className={styles.footerExplore} aria-label={en ? "Method, curriculum and Phuket" : "Метод, программа и Пхукет"}>
          <Link href={en ? "/en/method" : "/method"}>{en ? "Method" : "Метод"}</Link>
          <Link href={en ? "/en/curriculum" : "/curriculum"}>{en ? "Curriculum" : "Программа"}</Link>
          <Link href={en ? "/en/phuket" : "/phuket"}>{en ? "Phuket" : "Пхукет"}</Link>
        </nav>
        <span>© 2026</span>
      </footer>
    </div>
  );
}
