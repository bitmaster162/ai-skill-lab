import Link from "next/link";
import { Logo } from "./Logo";

export function Header({ contactHref = "/#contact" }: { contactHref?: string }) {
  return (
    <header className="siteHeader">
      <div className="shell headerInner">
        <Logo />
        <nav className="desktopNav" aria-label="Основная навигация">
          <Link href="/#programs">Программы</Link>
          <Link href="/kids">Дети</Link>
          <Link href="/#format">Формат</Link>
          <Link href="/#pricing">Стоимость</Link>
          <Link href="/#faq">FAQ</Link>
        </nav>
        <Link className="button buttonSmall buttonGhost" href={contactHref}>
          Подобрать программу
        </Link>
      </div>
    </header>
  );
}
