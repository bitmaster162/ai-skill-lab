import Script from "next/script";

/** Dormant until the separate E3.8 receiver/SQLite rollout is approved. */
export function UniverseEventRuntime() {
  return <Script id="phuket-universe-events" src="/phuket-universe-events.js"
    strategy="afterInteractive" />;
}
