import Link from "next/link";
import { Logo } from "./Logo";

export function Footer() {
  return (
    <footer className="footer">
      <div className="shell footerGrid">
        <div>
          <Logo />
          <p className="footerText">Практические AI-навыки для работы, учёбы и собственных проектов.</p>
        </div>
        <div className="footerLinks">
          <Link href="/#programs">Программы</Link>
          <Link href="/kids">Для детей</Link>
          <Link href="/#contact">Заявка</Link>
        </div>
        <div className="footerLegal">
          <span>© {new Date().getFullYear()} AI Academy</span>
          <span>Для несовершеннолетних заявку оставляет родитель или законный представитель.</span>
        </div>
      </div>
    </footer>
  );
}
