import Link from "next/link";
import { Logo } from "./Logo";

type Locale = "ru" | "en";

export function Footer({ locale = "ru" }: { locale?: Locale }) {
  const en = locale === "en";
  const base = en ? "/en" : "";
  return (
    <footer className="footer">
      <div className="shell footerGrid">
        <div>
          <Logo href={base || "/"} />
          <p className="footerText">
            {en
              ? "Practical AI skills for work, study and independent projects."
              : "Практические AI-навыки для работы, учёбы и собственных проектов."}
          </p>
        </div>
        <div className="footerLinks">
          <Link href={`${base}/#programs`}>{en ? "Programs" : "Программы"}</Link>
          <Link href={`${base}/kids`}>{en ? "Kids 8–13" : "Дети 8–13"}</Link>
          <Link href={`${base}/teens`}>{en ? "Teens 14–18" : "Подростки 14–18"}</Link>
          <Link href={`${base}/#contact`}>{en ? "Contact" : "Заявка"}</Link>
        </div>
        <div className="footerLegal">
          <span>© {new Date().getFullYear()} AI Skill Lab</span>
          <span>{en ? "A parent or legal guardian submits applications for minors." : "Для несовершеннолетних заявку оставляет родитель или законный представитель."}</span>
          <span>{en ? "Service-specific age requirements are checked before use." : "Возрастные требования конкретных AI-сервисов проверяются перед использованием."}</span>
        </div>
      </div>
    </footer>
  );
}
