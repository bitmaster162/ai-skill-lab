/* Universe click counter R7: DISABLED until D1 schema and receiver rollout. */
(() => {
  "use strict";
  const ENABLED = false; // production authority remains false
  if (!ENABLED || globalThis.__phuketUniverseEventsInstalled) return;
  globalThis.__phuketUniverseEventsInstalled = true;
  const allowed = new Set(["universe_click", "project_click", "listing_click"]);
  const projects = new Set([
    "phuketravel.vercel.app", "stasph.vercel.app",
    "muaithaiph.vercel.app", "haven-ruddy.vercel.app",
    "rostikson-portfolio.vercel.app",
  ]);
  document.addEventListener("click", (click) => {
    const anchor = click.target?.closest?.("a[data-universe-event]");
    if (!anchor) return;
    const event = anchor.getAttribute("data-universe-event");
    if (!allowed.has(event)) return;
    const href = anchor.getAttribute("href") || "";
    let target;
    try { target = new URL(href, location.origin); } catch { return; }
    if (event === "universe_click") {
      if (target.origin !== location.origin
          || !["/phuket-universe", "/en/phuket-universe"].includes(target.pathname)) return;
    } else if (event === "project_click") {
      if (target.protocol !== "https:" || !projects.has(target.hostname)
          || !anchor.closest("#orbit")) return;
    } else if (event === "listing_click") {
      if (target.protocol !== "https:" || !anchor.closest("#homes [data-u2-card]")) return;
    }
    const locale = document.documentElement.lang === "en" ? "en" : "ru";
    const page = location.pathname.replace(/\/+$/, "") || "/";
    if (page.length > 180 || !page.startsWith("/") || page.startsWith("//")
        || page.includes("?") || page.includes("#")) return;
    void fetch("/api/event", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      credentials: "omit",
      keepalive: true,
      cache: "no-store",
      body: JSON.stringify({event, page, locale}),
    }).catch(() => undefined);
  });
})();
