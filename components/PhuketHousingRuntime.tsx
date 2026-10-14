"use client";

import Script from "next/script";

/** Same-origin enhancement only; reruns on Next navigation, never queries data. */
export function PhuketHousingRuntime() {
  return <Script id="phuket-housing-u2" src="/phuket-housing-u2.js" strategy="afterInteractive"
    onReady={() => { document.dispatchEvent(new Event("phuket-housing:ready")); }} />;
}
