"use client";

import { usePathname, useSearchParams } from "next/navigation";
import { diagnosticApplicationHref, startInquiryProgram } from "@/lib/diagnostic-intent";
import styles from "./WorkshopShell.module.css";

type Props = { targetLocale: "ru" | "en"; alternateHref: string };

export function StartLanguageLink({ targetLocale, alternateHref }: Props) {
  const pathname = usePathname();
  const params = useSearchParams();
  const href = startInquiryProgram(pathname, params) === "diagnostic"
    ? diagnosticApplicationHref(targetLocale)
    : alternateHref;
  return <a className={styles.utility} href={href} referrerPolicy="no-referrer">{targetLocale.toUpperCase()}</a>;
}
