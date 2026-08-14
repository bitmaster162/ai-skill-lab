import Link from "next/link";

export function Logo() {
  return (
    <Link href="/" className="logo" aria-label="AI Academy — на главную">
      <span className="logoMark" aria-hidden="true">A</span>
      <span>AI Academy</span>
    </Link>
  );
}
