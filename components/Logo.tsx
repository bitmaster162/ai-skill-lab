import Link from "next/link";

export function Logo({ href = "/" }: { href?: string }) {
  return (
    <Link href={href} className="logo" aria-label="AI Skill Lab">
      <span className="logoMark" aria-hidden="true">A</span>
      <span className="logoText"><b>AI</b> SKILL LAB</span>
    </Link>
  );
}
